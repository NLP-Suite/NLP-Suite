import AppKit
import Foundation

struct Environment: Hashable {
    let folder: URL
    let python: URL

    var name: String {
        folder.lastPathComponent
    }

    var label: String {
        if isPackagedEnvironment(folder, architecture: currentMacArchitecture()) {
            return "Portable Python — \(shortPath(folder.path))"
        }
        return "\(name) — \(shortPath(folder.path))"
    }
}

struct PackageCheck: Decodable {
    let module: String
    let ok: Bool
    let version: String
    let error: String
}

struct CheckReport: Decodable {
    let python: String
    let pythonVersion: String
    let architecture: String
    let suite: String
    let checks: [PackageCheck]
    let declaredCount: Int
    let declaredMissing: [String]
    let lookupErrors: [String: String]
    let parseErrors: [String]

    var importantChecksPass: Bool {
        checks.allSatisfy(\.ok)
    }

    func score(for macArchitecture: String) -> Int {
        let architectureScore = architecture == macArchitecture ? 100_000 : 0
        let packageScore = checks.filter(\.ok).count * 1_000
        let sourceScore = max(0, declaredCount - declaredMissing.count)
        return architectureScore + packageScore + sourceScore
    }
}

struct CommandOutput {
    let status: Int32
    let text: String
}

let portableEnvironmentPreparedKey = "portableEnvironmentPreparedSuites"

func appendPath(_ relativePath: String, to base: URL) -> URL {
    relativePath.split(separator: "/").reduce(base.standardizedFileURL) { url, component in
        url.appendingPathComponent(String(component))
    }.standardizedFileURL
}

func uniqueURLs(_ urls: [URL]) -> [URL] {
    var seen = Set<String>()
    var unique: [URL] = []
    for url in urls {
        let standardized = url.standardizedFileURL
        if seen.insert(standardized.path).inserted {
            unique.append(standardized)
        }
    }
    return unique
}

func isPackagedEnvironment(_ folder: URL, architecture: String) -> Bool {
    folder.standardizedFileURL.lastPathComponent == "python-env"
}

func shortPath(_ path: String) -> String {
    let home = FileManager.default.homeDirectoryForCurrentUser.path
    if path == home {
        return "~"
    }
    if path.hasPrefix(home + "/") {
        return "~" + path.dropFirst(home.count)
    }
    return path
}

func findPython(in folder: URL) -> URL? {
    let choices = [
        folder.appendingPathComponent("bin/python3"),
        folder.appendingPathComponent("bin/python"),
    ]
    return choices.first { FileManager.default.fileExists(atPath: $0.path) }
}

func bundledEnvironmentFolder(in suite: URL) -> URL {
    suite.appendingPathComponent("python-env").standardizedFileURL
}

func bundledEnvironment(in suite: URL) -> Environment? {
    let folder = bundledEnvironmentFolder(in: suite)
    guard let python = findPython(in: folder) else {
        return nil
    }
    return Environment(folder: folder, python: python)
}

func findEnvironmentFolder(under folder: URL) -> URL? {
    if findPython(in: folder) != nil {
        return folder.standardizedFileURL
    }

    let children = try? FileManager.default.contentsOfDirectory(
        at: folder,
        includingPropertiesForKeys: [.isDirectoryKey],
        options: [.skipsHiddenFiles]
    )
    return children?.first { findPython(in: $0) != nil }?.standardizedFileURL
}

func run(
    _ executable: URL,
    _ arguments: [String],
    environment: [String: String]? = nil,
    folder: URL? = nil
) throws -> CommandOutput {
    let outputFile = FileManager.default.temporaryDirectory
        .appendingPathComponent("nlp-mac-setup-\(UUID().uuidString).txt")
    FileManager.default.createFile(atPath: outputFile.path, contents: nil)
    let outputHandle = try FileHandle(forWritingTo: outputFile)

    defer {
        try? outputHandle.close()
        try? FileManager.default.removeItem(at: outputFile)
    }

    let process = Process()
    process.executableURL = executable
    process.arguments = arguments
    process.environment = environment
    process.currentDirectoryURL = folder
    process.standardOutput = outputHandle
    process.standardError = outputHandle
    try process.run()
    process.waitUntilExit()
    try outputHandle.synchronize()

    let data = try Data(contentsOf: outputFile)
    return CommandOutput(
        status: process.terminationStatus,
        text: String(decoding: data, as: UTF8.self)
    )
}

func currentMacArchitecture() -> String {
    let uname = URL(fileURLWithPath: "/usr/bin/uname")
    let result = try? run(uname, ["-m"])
    return result?.text.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
}

func environmentVariables(for environment: Environment) -> [String: String] {
    var values = ProcessInfo.processInfo.environment
    let environmentBin = environment.folder.appendingPathComponent("bin").path
    let suiteFolder = environment.folder.deletingLastPathComponent()
    let suiteInternal = suiteFolder.appendingPathComponent("_internal")
    let environmentLib = environment.folder.appendingPathComponent("lib")
    let commonBins = ["/usr/bin", "/bin", "/usr/sbin", "/sbin", "/opt/homebrew/bin", "/usr/local/bin"]
    let launcherResources = Bundle.main.resourceURL?.path ?? ""
    let libraryPaths = [suiteInternal.path, environmentLib.path]
        .filter { FileManager.default.fileExists(atPath: $0) }

    values["PATH"] = ([environmentBin] + commonBins).joined(separator: ":")
    values["VIRTUAL_ENV"] = environment.folder.path
    values["DYLD_LIBRARY_PATH"] = (libraryPaths + [values["DYLD_LIBRARY_PATH"]].compactMap { $0 })
        .joined(separator: ":")
    values["PYTHONNOUSERSITE"] = "1"
    values["PYTHONPATH"] = launcherResources
    values["NLP_SUITE_SKIP_PACKAGE_CHECKS"] = "1"
    values["PAFY_BACKEND"] = "internal"
    values["NUMBA_CACHE_DIR"] = FileManager.default.temporaryDirectory
        .appendingPathComponent("nlp-mac-setup-numba-\(getuid())").path
    values["MPLCONFIGDIR"] = FileManager.default.temporaryDirectory
        .appendingPathComponent("nlp-mac-setup-matplotlib-\(getuid())").path
    values.removeValue(forKey: "PYTHONHOME")
    return values
}

final class AppDelegate: NSObject, NSApplicationDelegate {
    private var window: NSWindow!
    private var suiteField: NSTextField!
    private var environmentMenu: NSPopUpButton!
    private var statusLabel: NSTextField!
    private var progress: NSProgressIndicator!
    private var logView: NSTextView!
    private var executableQuarantineButton: NSButton!
    private var buttons: [NSButton] = []
    private var environments: [Environment] = []
    private var reports: [URL: CheckReport] = [:]
    private let macArchitecture = currentMacArchitecture()

    func applicationDidFinishLaunching(_ notification: Notification) {
        makeWindow()
        restoreLastFolder()
        scanForEnvironments()
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        true
    }

    private func makeWindow() {
        window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 820, height: 620),
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )
        window.title = "NLP Suite Mac Setup"
        window.center()
        window.minSize = NSSize(width: 720, height: 560)

        let content = NSView()
        window.contentView = content

        let title = NSTextField(labelWithString: "NLP Suite Mac Setup")
        title.font = .systemFont(ofSize: 26, weight: .semibold)

        let directions = NSTextField(
            wrappingLabelWithString:
                "1. Locate the NLP folder.  2. Verify the python environment.  3. Open the Suite."
        )
        directions.font = .systemFont(ofSize: 13)
        directions.textColor = .secondaryLabelColor

        suiteField = NSTextField()
        suiteField.placeholderString = "No folder chosen"
        suiteField.isEditable = false
        suiteField.lineBreakMode = .byTruncatingMiddle

        environmentMenu = NSPopUpButton()
        environmentMenu.target = self
        environmentMenu.action = #selector(environmentChanged)

        let chooseSuiteButton = makeButton("Choose Folder…", action: #selector(chooseSuite))
        let rescanButton = makeButton("Rescan", action: #selector(rescan))
        let checkButton = makeButton("Check This Setup", action: #selector(checkSelectedEnvironment))
        let openButton = makeButton("Open NLP Suite", action: #selector(openSuite), defaultButton: true)
        executableQuarantineButton = makeButton(
            "Remove Quarantine from Executable",
            action: #selector(removeExecutableQuarantine)
        )
        let folderQuarantineButton = makeButton(
            "Remove Quarantine from Whole Folder",
            action: #selector(removeFolderQuarantine)
        )

        buttons = [
            chooseSuiteButton,
            rescanButton,
            checkButton,
            openButton,
            executableQuarantineButton,
            folderQuarantineButton,
        ]

        statusLabel = NSTextField(labelWithString: "Choose the NLP Suite folder.")
        statusLabel.font = .systemFont(ofSize: 13, weight: .medium)

        progress = NSProgressIndicator()
        progress.style = .spinning
        progress.controlSize = .small
        progress.isDisplayedWhenStopped = false

        logView = NSTextView()
        logView.isEditable = false
        logView.font = .monospacedSystemFont(ofSize: 12, weight: .regular)
        logView.textContainerInset = NSSize(width: 10, height: 10)
        logView.string = "Choose the NLP Suite folder to begin.\n"

        let logScroll = NSScrollView()
        logScroll.documentView = logView
        logScroll.hasVerticalScroller = true
        logScroll.borderType = .bezelBorder

        let suiteRow = makeRow(
            label: "NLP Suite folder",
            control: suiteField,
            buttons: [chooseSuiteButton]
        )
        let environmentRow = makeRow(
            label: "Portable Python",
            control: environmentMenu,
            buttons: [rescanButton]
        )

        let actionRow = NSStackView(views: [checkButton, openButton])
        actionRow.orientation = .horizontal
        actionRow.spacing = 10

        let quarantineRow = NSStackView(views: [executableQuarantineButton, folderQuarantineButton])
        quarantineRow.orientation = .horizontal
        quarantineRow.spacing = 10

        let statusRow = NSStackView(views: [progress, statusLabel])
        statusRow.orientation = .horizontal
        statusRow.spacing = 8

        let separator = NSBox()
        separator.boxType = .separator

        let stack = NSStackView(views: [
            title,
            directions,
            separator,
            suiteRow,
            environmentRow,
            actionRow,
            quarantineRow,
            statusRow,
            logScroll,
        ])
        stack.orientation = .vertical
        stack.alignment = .leading
        stack.spacing = 14
        stack.translatesAutoresizingMaskIntoConstraints = false

        content.addSubview(stack)
        NSLayoutConstraint.activate([
            stack.leadingAnchor.constraint(equalTo: content.leadingAnchor, constant: 24),
            stack.trailingAnchor.constraint(equalTo: content.trailingAnchor, constant: -24),
            stack.topAnchor.constraint(equalTo: content.topAnchor, constant: 22),
            stack.bottomAnchor.constraint(equalTo: content.bottomAnchor, constant: -22),
            directions.widthAnchor.constraint(equalTo: stack.widthAnchor),
            suiteRow.widthAnchor.constraint(equalTo: stack.widthAnchor),
            environmentRow.widthAnchor.constraint(equalTo: stack.widthAnchor),
            statusRow.widthAnchor.constraint(equalTo: stack.widthAnchor),
            logScroll.widthAnchor.constraint(equalTo: stack.widthAnchor),
            logScroll.heightAnchor.constraint(greaterThanOrEqualToConstant: 250),
        ])

        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
    }

    private func makeButton(_ title: String, action: Selector, defaultButton: Bool = false) -> NSButton {
        let button = NSButton(title: title, target: self, action: action)
        button.bezelStyle = .rounded
        if defaultButton {
            button.keyEquivalent = "\r"
        }
        return button
    }

    private func makeRow(label: String, control: NSView, buttons: [NSButton]) -> NSStackView {
        let labelView = NSTextField(labelWithString: label)
        labelView.font = .systemFont(ofSize: 13, weight: .medium)
        labelView.widthAnchor.constraint(equalToConstant: 130).isActive = true

        control.setContentHuggingPriority(.defaultLow, for: .horizontal)
        control.setContentCompressionResistancePriority(.defaultLow, for: .horizontal)

        let row = NSStackView(views: [labelView, control] + buttons)
        row.orientation = .horizontal
        row.alignment = .centerY
        row.spacing = 10
        return row
    }

    private func restoreLastFolder() {
        let savedFolder = UserDefaults.standard.string(forKey: "suitePath").map {
            URL(fileURLWithPath: $0).standardizedFileURL
        }
        let folder = ([savedFolder].compactMap { $0 } + nearbySuiteCandidates()).first(where: isSuiteFolder)
        guard let folder else {
            return
        }

        UserDefaults.standard.set(folder.path, forKey: "suitePath")
        suiteField.stringValue = folder.path
        updateExecutableQuarantineButtonState()
    }

    private func nearbySuiteCandidates() -> [URL] {
        let appFolder = Bundle.main.bundleURL.deletingLastPathComponent().standardizedFileURL
        let bases = uniqueURLs([
            appFolder,
            appFolder.deletingLastPathComponent(),
            appFolder.deletingLastPathComponent().deletingLastPathComponent(),
        ])
        let names = [
            "NLP-Suite-mac-\(macArchitecture)",
            "NLP-Suite-mac-arm64",
            "NLP-Suite-mac-x86_64",
        ]

        return uniqueURLs(bases.flatMap { base in
            names.map { base.appendingPathComponent($0).standardizedFileURL }
        })
    }

    private func rememberSuiteFolder(_ folder: URL) {
        if isSuiteFolder(folder) {
            UserDefaults.standard.set(folder.standardizedFileURL.path, forKey: "suitePath")
            suiteField.stringValue = folder.path
            updateExecutableQuarantineButtonState()
        }
    }

    private func isSuiteFolder(_ folder: URL) -> Bool {
        let executable = folder.appendingPathComponent("NLP_Suite")
        let source = folder.appendingPathComponent("src")
        let portablePython = bundledEnvironmentFolder(in: folder)
        return FileManager.default.fileExists(atPath: executable.path)
            && FileManager.default.fileExists(atPath: source.path)
            && findPython(in: portablePython) != nil
    }

    private var selectedSuite: URL? {
        let path = suiteField.stringValue.trimmingCharacters(in: .whitespacesAndNewlines)
        return path.isEmpty ? nil : URL(fileURLWithPath: path).standardizedFileURL
    }

    private var selectedEnvironment: Environment? {
        let index = environmentMenu.indexOfSelectedItem
        return environments.indices.contains(index) ? environments[index] : nil
    }

    private func setBusy(_ busy: Bool, message: String) {
        statusLabel.stringValue = message
        buttons.forEach { $0.isEnabled = !busy }
        environmentMenu.isEnabled = !busy && !environments.isEmpty
        if !busy {
            updateExecutableQuarantineButtonState()
        }
        busy ? progress.startAnimation(nil) : progress.stopAnimation(nil)
    }

    private func addLog(_ text: String) {
        let time = DateFormatter.localizedString(from: Date(), dateStyle: .none, timeStyle: .medium)
        logView.textStorage?.append(NSAttributedString(string: "[\(time)] \(text)\n"))
        logView.scrollToEndOfDocument(nil)
    }

    private func showError(_ title: String, _ message: String) {
        let alert = NSAlert()
        alert.alertStyle = .critical
        alert.messageText = title
        alert.informativeText = message
        alert.runModal()
    }

    @objc private func chooseSuite() {
        let panel = NSOpenPanel()
        panel.title = "Choose the folder containing NLP_Suite"
        panel.canChooseDirectories = true
        panel.canChooseFiles = false
        panel.allowsMultipleSelection = false

        guard panel.runModal() == .OK, let folder = panel.url else {
            return
        }
        guard isSuiteFolder(folder) else {
            showError(
                "That is not the NLP Suite folder",
                "Choose the folder that directly contains NLP_Suite, src, and python-env/bin/python3."
            )
            return
        }

        rememberSuiteFolder(folder)
        reports.removeAll()
        addLog("Folder: \(shortPath(folder.path))")
        scanForEnvironments()
    }

    @objc private func chooseEnvironment() {
        let panel = NSOpenPanel()
        panel.title = "Choose a portable Python environment folder"
        panel.canChooseDirectories = true
        panel.canChooseFiles = false
        panel.allowsMultipleSelection = false

        guard panel.runModal() == .OK, let folder = panel.url else {
            return
        }
        guard let python = findPython(in: folder) else {
            showError(
                "That is not a Python environment",
                "Choose a folder that contains bin/python3 or bin/python."
            )
            return
        }

        let environment = Environment(folder: folder.standardizedFileURL, python: python)
        if !environments.contains(environment) {
            environments.append(environment)
            environments.sort(by: environmentComesFirst)
        }
        reloadEnvironmentMenu(preferred: environment.folder)
        saveSelectedEnvironment()
        addLog("Environment: \(shortPath(environment.folder.path))")
    }

    @objc private func rescan() {
        scanForEnvironments()
    }

    @objc private func environmentChanged() {
        saveSelectedEnvironment()
        guard let environment = selectedEnvironment else {
            return
        }
        if let report = reports[environment.folder] {
            showReport(report)
        } else {
            statusLabel.stringValue = "Environment chosen. Click Check This Setup."
        }
    }

    private func saveSelectedEnvironment() {
        if let environment = selectedEnvironment {
            UserDefaults.standard.set(environment.folder.path, forKey: "environmentPath")
        }
    }

    private func scanForEnvironments() {
        guard let suite = selectedSuite else {
            environments = []
            reloadEnvironmentMenu(preferred: nil)
            statusLabel.stringValue = "Choose the NLP Suite folder."
            return
        }

        setBusy(true, message: "Looking for bundled Python…")

        DispatchQueue.global(qos: .userInitiated).async {
            let found = self.findEnvironments(for: suite)
            DispatchQueue.main.async {
                self.environments = found
                let preferredURL = found.first?.folder
                self.reloadEnvironmentMenu(preferred: preferredURL)
                self.saveSelectedEnvironment()
                self.setBusy(
                    false,
                    message: found.isEmpty
                        ? "Bundled Python not found in this NLP Suite folder."
                        : "Using bundled Python."
                )
                self.addLog(
                    found.isEmpty
                        ? "No bundled Python found."
                        : "Python Env: \(shortPath(found[0].python.path))"
                )
            }
        }
    }

    private func findEnvironments(for suite: URL) -> [Environment] {
        bundledEnvironment(in: suite).map { [$0] } ?? []
    }

    private func environmentComesFirst(_ left: Environment, _ right: Environment) -> Bool {
        return left.folder.path.localizedStandardCompare(right.folder.path) == .orderedAscending
    }

    private func reloadEnvironmentMenu(preferred: URL?) {
        environmentMenu.removeAllItems()
        environmentMenu.addItems(withTitles: environments.map(\.label))

        if let preferred,
           let index = environments.firstIndex(where: { $0.folder == preferred.standardizedFileURL }) {
            environmentMenu.selectItem(at: index)
        } else if !environments.isEmpty {
            environmentMenu.selectItem(at: 0)
        }

        environmentMenu.isEnabled = !environments.isEmpty
    }

    private func preparedPortableEnvironments() -> Set<String> {
        Set(UserDefaults.standard.stringArray(forKey: portableEnvironmentPreparedKey) ?? [])
    }

    private func markPortableEnvironmentPrepared(_ environment: Environment) {
        var prepared = preparedPortableEnvironments()
        prepared.insert(environment.folder.standardizedFileURL.path)
        UserDefaults.standard.set(Array(prepared).sorted(), forKey: portableEnvironmentPreparedKey)
    }

    private func prepareEnvironmentIfNeeded(_ environment: Environment) throws {
        markPortableEnvironmentPrepared(environment)
    }

    @objc private func checkSelectedEnvironment() {
        guard let suite = selectedSuite, isSuiteFolder(suite) else {
            showError("Choose the NLP Suite folder", "Click Choose Folder… first.")
            return
        }
        guard let environment = selectedEnvironment else {
            showError("Bundled Python not found", "Choose the portable NLP Suite folder that contains python-env/bin/python3.")
            return
        }

        UserDefaults.standard.set(suite.path, forKey: "suitePath")
        saveSelectedEnvironment()
        setBusy(true, message: "Checking \(environment.name)…")
        addLog("Checking \(shortPath(environment.folder.path))")

        DispatchQueue.global(qos: .userInitiated).async {
            let result: Result<CheckReport, Error>
            do {
                self.allowMacToOpen(suite)
                try self.prepareEnvironmentIfNeeded(environment)
                result = self.check(environment: environment, suite: suite)
            } catch {
                result = .failure(error)
            }
            DispatchQueue.main.async {
                switch result {
                case .success(let report):
                    self.reports[environment.folder] = report
                    self.showReport(report)
                case .failure(let error):
                    self.setBusy(false, message: "Check failed.")
                    self.addLog(error.localizedDescription)
                    self.showError("Check failed", error.localizedDescription)
                }
            }
        }
    }

    private func check(environment: Environment, suite: URL) -> Result<CheckReport, Error> {
        guard
            let probe = Bundle.main.resourceURL?.appendingPathComponent("environment_probe.py"),
            FileManager.default.fileExists(atPath: probe.path)
        else {
            return .failure(
                NSError(
                    domain: "NLPSetup",
                    code: 1,
                    userInfo: [NSLocalizedDescriptionKey: "The setup checker is missing."]
                )
            )
        }

        do {
            let output = try run(
                environment.python,
                [probe.path, "--suite", suite.path],
                environment: environmentVariables(for: environment),
                folder: suite
            )

            guard output.status == 0 else {
                throw NSError(
                    domain: "NLPSetup",
                    code: Int(output.status),
                    userInfo: [NSLocalizedDescriptionKey: output.text]
                )
            }

            guard
                let jsonLine = output.text
                    .trimmingCharacters(in: .whitespacesAndNewlines)
                    .split(separator: "\n")
                    .last,
                let data = String(jsonLine).data(using: .utf8)
            else {
                throw NSError(
                    domain: "NLPSetup",
                    code: 2,
                    userInfo: [NSLocalizedDescriptionKey: "The setup checker returned no result."]
                )
            }

            return .success(try JSONDecoder().decode(CheckReport.self, from: data))
        } catch {
            return .failure(error)
        }
    }

    private func showReport(_ report: CheckReport) {
        var lines = [
            "Python: \(report.python)",
            "Python version: \(report.pythonVersion)",
            "Mac type: \(report.architecture)",
        ]

        for check in report.checks {
            if check.ok {
                let version = check.version.isEmpty ? "" : " \(check.version)"
                lines.append("✓ \(check.module)\(version)")
            } else {
                lines.append("✗ \(check.module): \(check.error)")
            }
        }

        if !report.declaredMissing.isEmpty {
            lines.append("Missing optional packages: \(report.declaredMissing.joined(separator: ", "))")
        }

        addLog(lines.joined(separator: "\n"))

        if report.architecture != macArchitecture {
            setBusy(
                false,
                message: "Wrong Mac type: environment is \(report.architecture), Mac is \(macArchitecture)."
            )
        } else if report.importantChecksPass {
            setBusy(
                false,
                message: report.declaredMissing.isEmpty
                    ? "Ready to open NLP Suite."
                    : "Ready for main tools. Some optional packages are missing."
            )
        } else {
            let failures = report.checks.filter { !$0.ok }.count
            setBusy(false, message: "Not ready: \(failures) important checks failed.")
        }
    }

    private func suiteMatchesThisMac(_ suite: URL) -> Bool {
        let executable = suite.appendingPathComponent("NLP_Suite")
        // Read the binary's architecture(s) straight from its Mach-O header instead of shelling out to
        // `lipo`. `/usr/bin/lipo` is an Xcode Command Line Tools stub: on a stock Mac WITHOUT the tools,
        // merely invoking it pops the "install Command Line Developer Tools" dialog -- which confused a
        // first-time user even though the Suite bundles its own Python and needs no developer tools.
        // Parsing the header needs no external process, so the launcher stays a click-through install.
        guard let archs = machOArchitectures(of: executable) else {
            return true  // unreadable -> stay permissive, exactly as the old lipo-failed path did
        }
        return archs.contains(macArchitecture)
    }

    /// Architectures of a Mach-O or universal ("fat") binary, parsed from its header bytes.
    /// Returns nil if the file can't be read or isn't recognizably Mach-O.
    private func machOArchitectures(of file: URL) -> [String]? {
        guard let data = try? Data(contentsOf: file, options: .mappedIfSafe), data.count >= 8 else {
            return nil
        }
        func be32(_ o: Int) -> UInt32 {
            return (UInt32(data[o]) << 24) | (UInt32(data[o + 1]) << 16)
                 | (UInt32(data[o + 2]) << 8) | UInt32(data[o + 3])
        }
        func le32(_ o: Int) -> UInt32 {
            return (UInt32(data[o + 3]) << 24) | (UInt32(data[o + 2]) << 16)
                 | (UInt32(data[o + 1]) << 8) | UInt32(data[o])
        }
        // Low 24 bits of a Mach-O cputype: 0x07 = x86_64, 0x0C = arm64 (0x01000000 64-bit flag stripped).
        func archName(_ cpuType: UInt32) -> String? {
            switch cpuType & 0x00ff_ffff {
            case 0x07: return "x86_64"
            case 0x0c: return "arm64"
            default:   return nil
            }
        }
        let magic = be32(0)
        if magic == 0xcafe_babe {                            // universal (fat), big-endian header
            let count = Int(be32(4))
            var archs: [String] = []
            var offset = 8                                   // first fat_arch; cputype is its first field
            for _ in 0..<count {
                guard offset + 4 <= data.count else { break }
                if let name = archName(be32(offset)) { archs.append(name) }
                offset += 20                                 // sizeof(fat_arch)
            }
            return archs.isEmpty ? nil : archs
        }
        if magic == 0xfeed_facf || magic == 0xfeed_face {    // thin Mach-O stored big-endian
            return archName(be32(4)).map { [$0] }
        }
        if magic == 0xcffa_edfe || magic == 0xcefa_edfe {    // thin Mach-O stored little-endian (native)
            return archName(le32(4)).map { [$0] }
        }
        return nil
    }

    private func allowMacToOpen(_ suite: URL) {
        let executable = suite.appendingPathComponent("NLP_Suite")
        let python3 = suite.appendingPathComponent("python-env/bin/python3")
        let python = suite.appendingPathComponent("python-env/bin/python")
        _ = try? run(
            URL(fileURLWithPath: "/usr/bin/xattr"),
            ["-dr", "com.apple.quarantine", suite.path]
        )
        for file in [executable, python3, python] {
            _ = try? run(
                URL(fileURLWithPath: "/bin/chmod"),
                ["+x", file.path]
            )
        }
    }

    private func updateExecutableQuarantineButtonState() {
        guard executableQuarantineButton != nil else {
            return
        }
        guard let suite = selectedSuite, isSuiteFolder(suite) else {
            executableQuarantineButton.title = "Remove Quarantine from Executable"
            executableQuarantineButton.isEnabled = false
            return
        }

        executableQuarantineButton.title = "Remove Quarantine from Executable"
        executableQuarantineButton.isEnabled = true
    }

    @objc private func removeExecutableQuarantine() {
        guard let suite = selectedSuite, isSuiteFolder(suite) else {
            showError("Choose the NLP Suite folder", "Click Choose Folder… first.")
            return
        }

        let executable = suite.appendingPathComponent("NLP_Suite")
        let xattr = URL(fileURLWithPath: "/usr/bin/xattr")
        let quarantine = try? run(xattr, ["-p", "com.apple.quarantine", executable.path])

        if quarantine?.status != 0 {
            statusLabel.stringValue = "NLP_Suite has no quarantine tag."
            addLog("No quarantine tag on \(shortPath(executable.path))")
            return
        }

        let result = try? run(xattr, ["-d", "com.apple.quarantine", executable.path])

        if result?.status == 0 {
            statusLabel.stringValue = "Quarantine removed from NLP_Suite."
            addLog("Removed quarantine from \(shortPath(executable.path))")
        } else {
            statusLabel.stringValue = "NLP_Suite had no quarantine tag, or removal failed."
            addLog(result?.text.trimmingCharacters(in: .whitespacesAndNewlines) ?? "xattr could not run.")
        }
    }

    @objc private func removeFolderQuarantine() {
        guard let suite = selectedSuite, isSuiteFolder(suite) else {
            showError("Choose the NLP Suite folder", "Click Choose Folder… first.")
            return
        }

        let result = try? run(
            URL(fileURLWithPath: "/usr/bin/xattr"),
            ["-c", "-r", suite.path],
            folder: suite
        )

        if result?.status == 0 {
            statusLabel.stringValue = "Quarantine and extended attributes removed from the whole folder."
            addLog("Cleared extended attributes from \(shortPath(suite.path))")
        } else {
            statusLabel.stringValue = "Could not clear the whole folder."
            addLog(result?.text.trimmingCharacters(in: .whitespacesAndNewlines) ?? "xattr could not run.")
        }
    }


    private func suiteEntryPointScript(in suite: URL) -> URL? {
        let candidates = [
            suite.appendingPathComponent("src/NLP_menu_main.py"),
            suite.appendingPathComponent("NLP_Suite.py"),
            suite.appendingPathComponent("src/NLP_Suite.py"),
            suite.appendingPathComponent("src/NLP_Suite_main.py"),
            suite.appendingPathComponent("src/NLP_welcome_main.py"),
        ]
        return candidates.first { FileManager.default.fileExists(atPath: $0.path) }
    }

    @objc private func openSuite() {
        guard let suite = selectedSuite, isSuiteFolder(suite) else {
            showError("Choose the NLP Suite folder", "Click Choose Folder… first.")
            return
        }
        guard let environment = selectedEnvironment else {
            showError("Bundled Python not found", "Choose the portable NLP Suite folder that contains python-env/bin/python3.")
            return
        }
        guard suiteMatchesThisMac(suite) else {
            showError(
                "Wrong NLP Suite download",
                macArchitecture == "arm64"
                    ? "This is an Apple Silicon Mac. Choose the ARM64 NLP Suite folder."
                    : "This is an Intel Mac. Choose the Intel NLP Suite folder."
            )
            return
        }

        if let report = reports[environment.folder] {
            guard report.importantChecksPass else {
                showError("This setup is not ready", "The bundled Python environment is missing required packages.")
                return
            }
            guard report.architecture == macArchitecture else {
                showError("Wrong Python type", "Choose an NLP Suite download made for this Mac.")
                return
            }
        }

        allowMacToOpen(suite)

        let logFolder = FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent("Library/Logs")
        try? FileManager.default.createDirectory(at: logFolder, withIntermediateDirectories: true)
        let logFile = logFolder.appendingPathComponent("NLP-Suite-Mac-Setup.log")
        FileManager.default.createFile(atPath: logFile.path, contents: nil)

        guard let entryPoint = suiteEntryPointScript(in: suite) else {
            showError(
                "NLP Suite entry script not found",
                "Could not find src/NLP_menu_main.py, NLP_Suite.py, or another known NLP Suite entry script in the selected folder."
            )
            addLog("No Python entry script found in \(shortPath(suite.path))")
            return
        }

        do {
            let logHandle = try FileHandle(forWritingTo: logFile)
            try logHandle.seekToEnd()

            let process = Process()
            process.executableURL = environment.python
            process.arguments = [entryPoint.path]
            process.currentDirectoryURL = suite
            try prepareEnvironmentIfNeeded(environment)
            process.environment = environmentVariables(for: environment)
            process.standardOutput = logHandle
            process.standardError = logHandle
            process.terminationHandler = { _ in
                try? logHandle.close()
            }
            try process.run()

            UserDefaults.standard.set(suite.path, forKey: "suitePath")
            saveSelectedEnvironment()
            addLog("Opened NLP Suite with \(environment.python.path)")
            statusLabel.stringValue = "NLP Suite is open."
        } catch {
            showError("NLP Suite did not open", error.localizedDescription)
            addLog(error.localizedDescription)
        }
    }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.setActivationPolicy(.regular)
app.run()
