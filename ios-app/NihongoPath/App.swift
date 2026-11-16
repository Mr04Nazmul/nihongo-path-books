import SwiftUI

@main struct NihongoPathApp: App {
    @StateObject private var session = Session()
    var body: some Scene {
        WindowGroup { RootView().environmentObject(session).tint(Color(red: 0.63, green: 0.19, blue: 0.34)) }
    }
}

struct RootView: View {
    @EnvironmentObject var session: Session
    @AppStorage("darkMode") private var dark = false
    var body: some View {
        TabView {
            NavigationStack { LibraryView() }.tabItem { Label("বই", systemImage: "books.vertical") }
            NavigationStack { AccountView() }.tabItem { Label("অ্যাকাউন্ট", systemImage: "person.crop.circle") }
            NavigationStack {
                Form {
                    Toggle("ডার্ক মোড", isOn: $dark)
                    Section("Nihongo Path Books") {
                        Text("বাংলায় জাপানি শিখুন • iOS")
                        Link("সহায়তা", destination: API.base.appendingPathComponent("support"))
                        Link("গোপনীয়তা", destination: API.base.appendingPathComponent("privacy"))
                        NavigationLink("লাইসেন্স ও কৃতজ্ঞতা") { ScrollView { Text(licenses).padding() } }
                    }
                }.navigationTitle("সেটিংস")
            }.tabItem { Label("সেটিংস", systemImage: "gearshape") }
        }
        .preferredColorScheme(dark ? .dark : .light)
        .task { await session.refresh() }
    }
    private var licenses: String {
        "Kanji stroke diagrams: KanjiVG © Ulrich Apel, CC BY-SA 3.0. https://kanjivg.tagaini.net\nhttps://creativecommons.org/licenses/by-sa/3.0/\n\nNoto fonts: SIL Open Font License 1.1. Full license texts are included in the app resources.\n\nReader and previews ported from the owner's Nihongo Path 1.19.3 maintenance backup."
    }
}

struct LibraryView: View {
    @EnvironmentObject var session: Session
    let levels = ["N5", "N4", "N3", "N2", "N1"]
    var body: some View {
        List {
            Section {
                VStack(alignment: .leading, spacing: 8) {
                    Text("日本語の旅").font(.largeTitle.bold())
                    Text("প্রতিদিন একটু করে জাপানি শিখুন").foregroundStyle(.secondary)
                }.padding(.vertical)
            }
            ForEach(levels, id: \.self) { level in
                Section(level) {
                    if level == "N1" { Label("Coming Soon", systemImage: "lock") }
                    else {
                        ForEach(["vocab", "grammar", "kanji"], id: \.self) { subject in
                            NavigationLink {
                                ReaderView(level: level, subject: subject, token: session.token, full: session.unlocked(level), studyState: session.studyState)
                                    .navigationTitle(title(subject)).navigationBarTitleDisplayMode(.inline)
                            } label: {
                                Label(title(subject), systemImage: subject == "kanji" ? "pencil.tip" : "book")
                            }
                        }
                        Text(session.unlocked(level) ? "পুরো বই খোলা আছে" : "বিনামূল্যের পাঠ • পূর্ণ বইয়ের জন্য অ্যাকাউন্টের access প্রয়োজন")
                            .font(.caption).foregroundStyle(.secondary)
                    }
                }
            }
        }.navigationTitle("Nihongo Path")
        .refreshable { await session.refresh() }
    }
    func title(_ subject: String) -> String {
        ["vocab": "শব্দভান্ডার", "grammar": "ব্যাকরণ", "kanji": "কানজি ও হাতের লেখা"][subject] ?? subject
    }
}

struct AccountView: View {
    @EnvironmentObject var session: Session
    @State private var email = ""
    @State private var password = ""
    @State private var name = ""
    @State private var registering = false
    @State private var deleting = false
    @State private var busy = false
    var body: some View {
        Form {
            if session.token.isEmpty {
                Picker("অ্যাকাউন্ট", selection: $registering) {
                    Text("লগইন").tag(false); Text("তৈরি করুন").tag(true)
                }.pickerStyle(.segmented)
                if registering { TextField("নাম", text: $name).textContentType(.name) }
                TextField("ইমেইল", text: $email).textInputAutocapitalization(.never)
                    .keyboardType(.emailAddress).textContentType(.emailAddress).autocorrectionDisabled()
                SecureField("পাসওয়ার্ড", text: $password).textContentType(registering ? .newPassword : .password)
                if registering { Text("পাসওয়ার্ড ১০–১২৮ অক্ষরের হতে হবে।").font(.caption) }
                Button(registering ? "অ্যাকাউন্ট তৈরি করুন" : "লগইন") {
                    busy = true
                    Task {
                        await session.authenticate(email: email, password: password, name: name, register: registering)
                        password = ""; busy = false
                    }
                }.disabled(busy || email.isEmpty || password.isEmpty)
                Button("Google দিয়ে লগইন") {
                    busy = true
                    Task { await session.signInWithGoogle(); busy = false }
                }.disabled(busy)
                Link("পাসওয়ার্ড ভুলে গেলে সহায়তা নিন", destination: API.base.appendingPathComponent("support"))
            } else {
                Section("আপনার অ্যাকাউন্ট") {
                    Text(session.name)
                    Button("Access রিফ্রেশ করুন") { Task { await session.refresh() } }
                    Button("লগআউট") { Task { await session.logout() } }
                }
                Section("বইয়ের access") {
                    ForEach(["N5", "N4", "N3", "N2"], id: \.self) { level in
                        HStack { Text(level); Spacer(); Text(session.unlocked(level) ? "খোলা" : "বিনামূল্যের পাঠ") }
                    }
                    Text("এই iOS build-এ rewarded বিজ্ঞাপন এখনো সক্রিয় নয়। আগে থেকে থাকা বৈধ unlock ব্যবহার করা যাবে।").font(.caption)
                }
                Button("অ্যাপ ডেটা মুছুন", role: .destructive) { deleting = true }
                    .confirmationDialog("Nihongo Path-এর অ্যাপ ডেটা মুছবেন? অন্য অ্যাপের shared login account থাকবে।", isPresented: $deleting, titleVisibility: .visible) {
                        Button("স্থায়ীভাবে মুছুন", role: .destructive) { Task { await session.deleteAccount() } }
                    }
            }
            if busy { ProgressView() }
            if !session.message.isEmpty { Text(session.message).foregroundStyle(.secondary) }
        }.navigationTitle("অ্যাকাউন্ট")
    }
}
