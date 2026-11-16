import Foundation
import AuthenticationServices
import CryptoKit
import Security
import UIKit

@MainActor final class GoogleSignIn: NSObject, ASWebAuthenticationPresentationContextProviding {
    private var browser: ASWebAuthenticationSession?
    func presentationAnchor(for session: ASWebAuthenticationSession) -> ASPresentationAnchor {
        UIApplication.shared.connectedScenes.compactMap { $0 as? UIWindowScene }.flatMap(\.windows).first(where: \.isKeyWindow) ?? ASPresentationAnchor()
    }
    func signIn() async throws -> [String: Any] {
        var bytes = [UInt8](repeating: 0, count: 32)
        guard SecRandomCopyBytes(kSecRandomDefault, bytes.count, &bytes) == errSecSuccess else { throw URLError(.cannotCreateFile) }
        let verifier = Self.base64(Data(bytes))
        let challenge = Self.base64(Data(SHA256.hash(data: Data(verifier.utf8))))
        let flow = UUID().uuidString.lowercased()
        let start = try await API.request("auth/google/start", method: "POST", body: ["challenge": challenge, "flow": flow])
        guard let raw = start["url"] as? String, let url = URL(string: raw), url.scheme == "https", url.host == API.base.host, url.path == "/auth/v1/authorize" else { throw URLError(.badURL) }
        let callback: URL = try await withCheckedThrowingContinuation { continuation in
            browser = ASWebAuthenticationSession(url: url, callbackURLScheme: "nihongopathbooks") { url, error in
                if let url { continuation.resume(returning: url) }
                else { continuation.resume(throwing: error ?? URLError(.cancelled)) }
            }
            browser?.presentationContextProvider = self
            if browser?.start() != true { continuation.resume(throwing: URLError(.cannotConnectToHost)) }
        }
        browser = nil
        let items = URLComponents(url: callback, resolvingAgainstBaseURL: false)?.queryItems ?? []
        guard callback.scheme == "nihongopathbooks", callback.host == "auth", callback.path == "/callback",
              items.first(where: { $0.name == "flow" })?.value == flow,
              let code = items.first(where: { $0.name == "code" })?.value else { throw URLError(.userAuthenticationRequired) }
        return try await API.request("auth/exchange", method: "POST", body: ["code": code, "verifier": verifier])
    }
    private static func base64(_ data: Data) -> String {
        data.base64EncodedString().replacingOccurrences(of: "+", with: "-").replacingOccurrences(of: "/", with: "_").replacingOccurrences(of: "=", with: "")
    }
}
