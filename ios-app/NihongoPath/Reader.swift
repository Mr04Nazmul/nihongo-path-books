import SwiftUI
import WebKit
import AVFoundation
import UniformTypeIdentifiers

struct ReaderView: UIViewControllerRepresentable {
    let level: String
    let subject: String
    let token: String
    let full: Bool
    let studyState: [String: Any]
    func makeUIViewController(context: Context) -> ReaderController {
        ReaderController(level: level, subject: subject, token: token, full: full, studyState: studyState)
    }
    func updateUIViewController(_ controller: ReaderController, context: Context) {}
    static func dismantleUIViewController(_ controller: ReaderController, coordinator: ()) { controller.close() }
}

final class ResourceHandler: NSObject, WKURLSchemeHandler {
    let root: URL
    init(root: URL) { self.root = root }
    func webView(_ webView: WKWebView, start urlSchemeTask: WKURLSchemeTask) {
        guard let url = urlSchemeTask.request.url, url.host == "reader" else {
            urlSchemeTask.didFailWithError(URLError(.unsupportedURL)); return
        }
        do {
            let file = try localFile(root: root, path: String(url.path.dropFirst()))
            let bytes = try Data(contentsOf: file)
            let mime = UTType(filenameExtension: file.pathExtension)?.preferredMIMEType ?? "application/octet-stream"
            urlSchemeTask.didReceive(URLResponse(url: url, mimeType: mime, expectedContentLength: bytes.count, textEncodingName: mime.hasPrefix("text/") ? "utf-8" : nil))
            urlSchemeTask.didReceive(bytes); urlSchemeTask.didFinish()
        } catch { urlSchemeTask.didFailWithError(error) }
    }
    func webView(_ webView: WKWebView, stop urlSchemeTask: WKURLSchemeTask) {}
}

func localFile(root: URL, path: String) throws -> URL {
    guard !path.isEmpty, !path.contains("\\"), !path.split(separator: "/").contains("..") else { throw URLError(.noPermissionsToReadFile) }
    let candidate = root.appendingPathComponent(path).standardizedFileURL.resolvingSymlinksInPath()
    guard candidate.path.hasPrefix(root.standardizedFileURL.resolvingSymlinksInPath().path + "/") else { throw URLError(.noPermissionsToReadFile) }
    return candidate
}

final class ReaderController: UIViewController, WKScriptMessageHandlerWithReply, WKNavigationDelegate {
    let level: String, subject: String, token: String
    let full: Bool
    let studyState: [String: Any]
    private let root = Bundle.main.resourceURL!.appendingPathComponent("reader", isDirectory: true)
    private var web: WKWebView!
    private let speech = AVSpeechSynthesizer()
    private var work: [UUID: Task<Void, Never>] = [:]
    init(level: String, subject: String, token: String, full: Bool, studyState: [String: Any]) {
        self.studyState = studyState
        self.level = level; self.subject = subject; self.token = token; self.full = full && !token.isEmpty && level != "N1"
        super.init(nibName: nil, bundle: nil)
    }
    required init?(coder: NSCoder) { fatalError("init(coder:) is not used") }
    override func viewDidLoad() {
        super.viewDidLoad()
        let config = WKWebViewConfiguration()
        config.websiteDataStore = .nonPersistent()
        config.setURLSchemeHandler(ResourceHandler(root: root), forURLScheme: "nihongo")
        config.userContentController.addScriptMessageHandler(self, contentWorld: .page, name: "native")
        let dark = UserDefaults.standard.bool(forKey: "darkMode")
        let access = "{preview:\(!full),remainingMs:2147483647}"
        let initialState = String(data: (try? JSONSerialization.data(withJSONObject: studyState)) ?? Data("{}".utf8), encoding: .utf8) ?? "{}"
        let script = """
        (()=>{
          localStorage.setItem('nihongo-path', JSON.stringify(\(initialState)));
          const send=(action,args=[])=>window.webkit.messageHandlers.native.postMessage({action,args});
          window.StudyNative={
            appearance:()=>JSON.stringify({dark:\(dark)}),
            readerAccess:()=>JSON.stringify(\(access)),
            speak:(...a)=>send('speak',a),stopSpeech:()=>send('stopSpeech'),
            unlock:()=>send('unlock'),navigate:()=>send('navigate'),
            saveProgress:(...a)=>send('saveProgress',a),recordReading:()=>{},
            selectStudyLevel:()=>send('level'),selectKanjiLevel:()=>send('level')
          };
          window.fetch=async function(input){
            const u=new URL(typeof input==='string'?input:input.url,location.href);
            if(u.protocol!=='nihongo:'||u.hostname!=='reader')throw new Error('External resource blocked');
            const r=await send('fetch',[u.pathname]);
            const bytes=Uint8Array.from(atob(r.base64),c=>c.charCodeAt(0));
            return new Response(bytes,{status:200,headers:{'Content-Type':r.mime}});
          };
          window.addEventListener('unhandledrejection',()=>{
            if(document.getElementById('ios-reader-error'))return;
            const e=document.createElement('p');e.id='ios-reader-error';e.textContent='পাঠ লোড হয়নি। ফিরে গিয়ে সংযোগ ও অ্যাকাউন্টের access পরীক্ষা করুন।';
            e.style.cssText='padding:16px;color:#a03156;background:#fff2f6';document.body.prepend(e);
          });
        })();
        """
        config.userContentController.addUserScript(WKUserScript(source: script, injectionTime: .atDocumentStart, forMainFrameOnly: true))
        web = WKWebView(frame: .zero, configuration: config)
        web.navigationDelegate = self
        view = web
        let page = subject == "kanji" ? "kanji.html" : "study.html"
        var url = URLComponents(string: "nihongo://reader/\(page)")!
        url.queryItems = [.init(name: "level", value: level), .init(name: "section", value: subject), .init(name: "preview", value: full ? "0" : "1")]
        web.load(URLRequest(url: url.url!))
    }
    func close() {
        speech.stopSpeaking(at: .immediate)
        for task in work.values { task.cancel() }; work.removeAll()
        web?.stopLoading(); web?.configuration.userContentController.removeScriptMessageHandler(forName: "native", contentWorld: .page)
    }
    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage, replyHandler: @escaping (Any?, String?) -> Void) {
        guard message.frameInfo.isMainFrame, message.frameInfo.request.url?.scheme == "nihongo",
              let body = message.body as? [String: Any], let action = body["action"] as? String else {
            replyHandler(nil, "Untrusted message"); return
        }
        let args = body["args"] as? [String] ?? []
        if action == "fetch", let raw = args.first {
            let id = UUID()
            work[id] = Task { @MainActor [weak self] in
                guard let self else { replyHandler(nil, "Reader closed"); return }
                do {
                    let result = try await self.resource(String(raw.drop(while: { $0 == "/" })))
                    if !Task.isCancelled { replyHandler(result, nil) }
                } catch { if !Task.isCancelled { replyHandler(nil, error.localizedDescription) } }
                self.work[id] = nil
            }
            return
        }
        switch action {
        case "speak":
            if let text = args.first, text.count < 10000 {
                speech.stopSpeaking(at: .immediate)
                let utterance = AVSpeechUtterance(string: text)
                utterance.voice = AVSpeechSynthesisVoice(language: "ja-JP"); utterance.rate = 0.42
                speech.speak(utterance)
            }
        case "stopSpeech": speech.stopSpeaking(at: .immediate)
        case "saveProgress":
            if !token.isEmpty, let raw = args.first, raw.utf8.count < 180000,
               let data = raw.data(using: .utf8), let state = try? JSONSerialization.jsonObject(with: data) as? [String: Any] {
                Task { @MainActor [weak self] in
                    guard let self else { return }
                    do { _ = try await API.request("study-state", method: "PUT", token: self.token, body: ["state": state]) }
                    catch { self.show("অগ্রগতি সেভ হয়নি। সংযোগ পরীক্ষা করুন।") }
                }
            }
        case "unlock": show("iOS rewarded বিজ্ঞাপন এখনো সক্রিয় হয়নি। বৈধ unlock থাকলে অ্যাকাউন্ট ট্যাব থেকে access রিফ্রেশ করুন।")
        case "level": show("অন্য লেভেল খুলতে বইয়ের মূল তালিকায় ফিরে যান।")
        case "navigate": show("KanjiVG © Ulrich Apel • CC BY-SA 3.0। বিস্তারিত সেটিংসের লাইসেন্স পাতায় আছে।")
        default: break
        }
        replyHandler(["ok": true], nil)
    }
    private func resource(_ path: String) async throws -> [String: String] {
        _ = try localFile(root: root, path: path)
        let protected = path.hasPrefix("data/") || path.hasPrefix("kanji/") || path.hasPrefix("strokes/")
        if protected {
            let lower = level.lowercased()
            let valid = path == "data/lessons-\(lower).json" || path == "kanji/\(lower).json" ||
                (path.hasPrefix("strokes/\(lower)/") && path.range(of: "^strokes/n[2-5]/[0-9a-f]{5}\\.json$", options: .regularExpression) != nil)
            guard valid else { throw URLError(.noPermissionsToReadFile) }
            if full {
                var request = URLRequest(url: API.base.appendingPathComponent("content").appendingPathComponent(path))
                request.timeoutInterval = 45; request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
                request.setValue("no-store", forHTTPHeaderField: "Cache-Control")
                let (data, response) = try await URLSession.shared.data(for: request)
                guard (response as? HTTPURLResponse)?.statusCode == 200 else { throw URLError(.userAuthenticationRequired) }
                return ["base64": data.base64EncodedString(), "mime": "application/json"]
            }
            let local = path.hasPrefix("data/") ? "previews/" + String(path.dropFirst(5)) : "previews/" + path
            let data = try Data(contentsOf: localFile(root: root, path: local))
            return ["base64": data.base64EncodedString(), "mime": "application/json"]
        }
        throw URLError(.noPermissionsToReadFile)
    }
    func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        let url = navigationAction.request.url
        let pages = ["/study.html", "/kanji.html"]
        let allowed = url?.scheme == "nihongo" && url?.host == "reader" && pages.contains(url?.path ?? "")
            && URLComponents(url: url!, resolvingAgainstBaseURL: false)?.queryItems?.first(where: { $0.name == "level" })?.value == level
        decisionHandler(allowed ? .allow : .cancel)
    }
    private func show(_ text: String) {
        guard presentedViewController == nil else { return }
        let alert = UIAlertController(title: "Nihongo Path", message: text, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "ঠিক আছে", style: .default)); present(alert, animated: true)
    }
}
