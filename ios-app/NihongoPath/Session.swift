import Foundation
import Combine
import Security

struct API {
    static let base = URL(string: "https://vjygltfnrmyghlwyjtwu.supabase.co/functions/v1/nihongo-books-v1")!
    static func request(_ path: String, method: String = "GET", token: String = "", body: [String: Any]? = nil) async throws -> [String: Any] {
        var request = URLRequest(url: base.appendingPathComponent(path))
        request.httpMethod = method
        request.timeoutInterval = 45
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("no-store", forHTTPHeaderField: "Cache-Control")
        if !token.isEmpty { request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization") }
        if let body { request.httpBody = try JSONSerialization.data(withJSONObject: body) }
        let (data, response) = try await URLSession.shared.data(for: request)
        let object = (try? JSONSerialization.jsonObject(with: data)) as? [String: Any] ?? [:]
        guard let http = response as? HTTPURLResponse, (200...299).contains(http.statusCode) else {
            throw NSError(domain: "NihongoPath", code: (response as? HTTPURLResponse)?.statusCode ?? 0,
                          userInfo: [NSLocalizedDescriptionKey: object["error"] as? String ?? "সার্ভারের সঙ্গে সংযোগ হয়নি। আবার চেষ্টা করুন।"])
        }
        return object
    }
}

enum Vault {
    static let service = "online.devnazu.books.ios.session"
    static func read() -> String {
        let query: [String: Any] = [kSecClass as String: kSecClassGenericPassword, kSecAttrService as String: service,
                                   kSecAttrAccount as String: "session", kSecReturnData as String: true, kSecMatchLimit as String: kSecMatchLimitOne]
        var result: CFTypeRef?
        guard SecItemCopyMatching(query as CFDictionary, &result) == errSecSuccess, let data = result as? Data else { return "" }
        return String(data: data, encoding: .utf8) ?? ""
    }
    static func save(_ value: String) throws {
        let query: [String: Any] = [kSecClass as String: kSecClassGenericPassword, kSecAttrService as String: service, kSecAttrAccount as String: "session"]
        if value.isEmpty { SecItemDelete(query as CFDictionary); return }
        let fields: [String: Any] = [kSecValueData as String: Data(value.utf8), kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly]
        var status = SecItemUpdate(query as CFDictionary, fields as CFDictionary)
        if status == errSecItemNotFound { status = SecItemAdd(query.merging(fields) { _, new in new } as CFDictionary, nil) }
        guard status == errSecSuccess else { throw NSError(domain: NSOSStatusErrorDomain, code: Int(status)) }
    }
}

@MainActor final class Session: ObservableObject {
    @Published var token = Vault.read()
    @Published var name = ""
    @Published var studyState: [String: Any] = {
        guard Vault.read().isEmpty, let data = UserDefaults.standard.data(forKey: "guestStudyState") else { return [:] }
        return (try? JSONSerialization.jsonObject(with: data)) as? [String: Any] ?? [:]
    }()
    @Published var message = ""
    private let google = GoogleSignIn()
    @Published private var expiries: [String: Date] = [:]
    func unlocked(_ level: String) -> Bool { (expiries[level] ?? .distantPast) > Date() }
    func saveLocalProgress(_ state: [String: Any]) {
        studyState = state
        if token.isEmpty, let data = try? JSONSerialization.data(withJSONObject: state) {
            UserDefaults.standard.set(data, forKey: "guestStudyState")
        }
    }
    func apply(_ object: [String: Any]) {
        name = (object["user"] as? [String: Any])?["name"] as? String ?? "Nihongo Path"
        studyState = object["studyState"] as? [String: Any] ?? [:]
        expiries = [:]
        let formatter = ISO8601DateFormatter()
        for row in object["unlocks"] as? [[String: Any]] ?? [] {
            if let level = row["level"] as? String, let raw = row["expires_at"] as? String {
                formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
                let fractional = formatter.date(from: raw)
                formatter.formatOptions = [.withInternetDateTime]
                expiries[level] = fractional ?? formatter.date(from: raw)
            }
        }
    }
    func authenticate(email: String, password: String, name: String, register: Bool) async {
        do {
            let object = try await API.request(register ? "auth/register" : "auth/login", method: "POST", body: ["email": email.trimmingCharacters(in: .whitespacesAndNewlines), "password": password, "name": name])
            guard let newToken = object["token"] as? String, !newToken.isEmpty else { throw URLError(.badServerResponse) }
            try Vault.save(newToken); token = newToken; apply(object); message = ""; await refresh()
        } catch { message = error.localizedDescription }
    }
    func signInWithGoogle() async {
        do {
            let object = try await google.signIn()
            guard let value = object["token"] as? String, !value.isEmpty else { throw URLError(.badServerResponse) }
            try Vault.save(value); token = value; apply(object); message = ""; await refresh()
        } catch { message = error.localizedDescription }
    }
    func refresh() async {
        guard !token.isEmpty else { return }
        do { apply(try await API.request("me", token: token)); message = "" }
        catch {
            expiries = [:]; message = error.localizedDescription
            if (error as NSError).code == 401 { clear() }
        }
    }
    func clear() { try? Vault.save(""); token = ""; expiries = [:]; name = ""; studyState = [:] }
    func logout() async {
        do { _ = try await API.request("auth/logout", method: "POST", token: token); clear(); message = "" }
        catch { message = error.localizedDescription }
    }
    func deleteAccount() async {
        do { _ = try await API.request("account", method: "DELETE", token: token); clear(); message = "অ্যাকাউন্ট মুছে দেওয়া হয়েছে।" }
        catch { message = error.localizedDescription }
    }
}
