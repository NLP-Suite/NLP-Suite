import AppKit
import Foundation

struct Environment: Hashable {
    let folder: URL
    let python: URL

    var name: String {
        folder.lastPathComponent
    }

    var label: String {
        "\(name) — \(shortPath(folder.path))"
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
    return choices.first { FileManager.default.isExecutableFile(atPath: $0.path) }
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
    let commonBins = ["/usr/bin", "/bin", "/usr/sbin", "/sbin", "/opt/homebrew/bin", "/usr/local/bin"]
    let launcherResources = Bundle.main.resourceURL?.path ?? ""

    values["PATH"] = ([environmentBin] + commonBins).joined(separator: ":")
    values["CONDA_PREFIX"] = environment.folder.path
    values["CONDA_DEFAULT_ENV"] = environment.name
    values["CONDA_SHLVL"] = "1"
    values["PYTHONNOUSERSITE"] = "1"
    values["PYTHONPATH"] = launcherResources
    values["NLP_SUITE_SKIP_PACKAGE_CHECKS"] = "1"
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
                "1. Choose the NLP Suite folder.  2. Find a working environment.  3. Check it.  4. Open NLP Suite."
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
        let chooseEnvironmentButton = makeButton("Choose…", action: #selector(chooseEnvironment))
        let findBestButton = makeButton("Find Best Automatically", action: #selector(findBestEnvironment))
        let checkButton = makeButton("Check This Setup", action: #selector(checkSelectedEnvironment))
        let openButton = makeButton("Open NLP Suite", action: #selector(openSuite), defaultButton: true)
        let executableQuarantineButton = makeButton(
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
            chooseEnvironmentButton,
            findBestButton,
            checkButton,
            openButton,
            executableQuarantineButton,
            folderQuarantineButton,
        ]

        statusLabel = NSTextField(labelWithString: "Looking for Conda environments…")
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
            label: "Conda environment",
            control: environmentMenu,
            buttons: [rescanButton, chooseEnvironmentButton]
        )

        let actionRow = NSStackView(views: [findBestButton, checkButton, openButton])
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
        guard let path = UserDefaults.standard.string(forKey: "suitePath") else {
            return
        }
        let folder = URL(fileURLWithPath: path)
        if isSuiteFolder(folder) {
            suiteField.stringValue = folder.path
        }
    }

    private func isSuiteFolder(_ folder: URL) -> Bool {
        let executable = folder.appendingPathComponent("NLP_Suite")
        let source = folder.appendingPathComponent("src")
        return FileManager.default.fileExists(atPath: executable.path)
            && FileManager.default.fileExists(atPath: source.path)
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
                "Choose the folder that directly contains NLP_Suite and the src folder."
            )
            return
        }

        suiteField.stringValue = folder.path
        UserDefaults.standard.set(folder.path, forKey: "suitePath")
        reports.removeAll()
        addLog("Folder: \(shortPath(folder.path))")
        statusLabel.stringValue = "Folder chosen. Click Find Best Automatically."
    }

    @objc private func chooseEnvironment() {
        let panel = NSOpenPanel()
        panel.title = "Choose a Conda environment folder"
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
        setBusy(true, message: "Looking for Conda environments…")

        DispatchQueue.global(qos: .userInitiated).async {
            let found = self.findEnvironments()
            DispatchQueue.main.async {
                self.environments = found
                let savedPath = UserDefaults.standard.string(forKey: "environmentPath")
                let savedURL = savedPath.map { URL(fileURLWithPath: $0) }
                self.reloadEnvironmentMenu(preferred: savedURL)
                self.setBusy(
                    false,
                    message: found.isEmpty
                        ? "No Conda environments found. Click Choose…"
                        : "Found \(found.count) Conda environments."
                )
                self.addLog(
                    found.isEmpty
                        ? "No environments found."
                        : "Found \(found.count) environments."
                )
            }
        }
    }

    private func findEnvironments() -> [Environment] {
        let files = FileManager.default
        let home = files.homeDirectoryForCurrentUser
        var folders = Set<URL>()

        if let activePath = ProcessInfo.processInfo.environment["CONDA_PREFIX"] {
            folders.insert(URL(fileURLWithPath: activePath).standardizedFileURL)
        }

        let roots = [
            home.appendingPathComponent("anaconda"),
            home.appendingPathComponent("anaconda3"),
            home.appendingPathComponent("miniconda"),
            home.appendingPathComponent("miniconda3"),
            home.appendingPathComponent("miniforge3"),
            home.appendingPathComponent("mambaforge"),
            URL(fileURLWithPath: "/opt/homebrew/Caskroom/miniconda/base"),
            URL(fileURLWithPath: "/opt/homebrew/Caskroom/miniforge/base"),
            URL(fileURLWithPath: "/opt/homebrew/anaconda3"),
            URL(fileURLWithPath: "/opt/anaconda3"),
            URL(fileURLWithPath: "/opt/miniconda3"),
            URL(fileURLWithPath: "/Applications/anaconda3"),
            URL(fileURLWithPath: "/Applications/miniconda3"),
            URL(fileURLWithPath: "/usr/local/anaconda3"),
            URL(fileURLWithPath: "/usr/local/miniconda3"),
            URL(fileURLWithPath: "/usr/local/Caskroom/miniconda/base"),
        ]

        let registry = home.appendingPathComponent(".conda/environments.txt")
        if let text = try? String(contentsOf: registry, encoding: .utf8) {
            for line in text.split(whereSeparator: \.isNewline) {
                let path = String(line).trimmingCharacters(in: .whitespacesAndNewlines)
                let folder = URL(fileURLWithPath: path).standardizedFileURL
                if findPython(in: folder) != nil {
                    folders.insert(folder)
                }
            }
        }

        for root in roots {
            if findPython(in: root) != nil {
                folders.insert(root.standardizedFileURL)
            }

            let envsFolder = root.appendingPathComponent("envs")
            let children = try? files.contentsOfDirectory(
                at: envsFolder,
                includingPropertiesForKeys: [.isDirectoryKey],
                options: [.skipsHiddenFiles]
            )
            for child in children ?? [] where findPython(in: child) != nil {
                folders.insert(child.standardizedFileURL)
            }
        }

        let condaPrograms = roots.map { $0.appendingPathComponent("bin/conda") } + [
            URL(fileURLWithPath: "/opt/homebrew/bin/conda"),
            URL(fileURLWithPath: "/usr/local/bin/conda"),
        ]

        for conda in condaPrograms where files.isExecutableFile(atPath: conda.path) {
            guard
                let output = try? run(conda, ["env", "list", "--json"]),
                output.status == 0,
                let data = output.text.data(using: .utf8),
                let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                let paths = json["envs"] as? [String]
            else {
                continue
            }

            for path in paths {
                let folder = URL(fileURLWithPath: path).standardizedFileURL
                if findPython(in: folder) != nil {
                    folders.insert(folder)
                }
            }
        }

        return folders.compactMap { folder in
            guard let python = findPython(in: folder) else {
                return nil
            }
            return Environment(folder: folder, python: python)
        }.sorted(by: environmentComesFirst)
    }

    private func environmentComesFirst(_ left: Environment, _ right: Environment) -> Bool {
        func priority(_ environment: Environment) -> Int {
            let isNLP = environment.name.caseInsensitiveCompare("NLP") == .orderedSame
            let isTraditionalInstall = environment.folder.path.contains("/anaconda/envs/NLP")
                || environment.folder.path.contains("/anaconda3/envs/NLP")
            if isNLP && isTraditionalInstall {
                return 0
            }
            if isNLP {
                return 1
            }
            if environment.name.localizedCaseInsensitiveContains("nlp") {
                return 2
            }
            return 3
        }

        let leftPriority = priority(left)
        let rightPriority = priority(right)
        if leftPriority != rightPriority {
            return leftPriority < rightPriority
        }
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

    @objc private func checkSelectedEnvironment() {
        guard let suite = selectedSuite, isSuiteFolder(suite) else {
            showError("Choose the NLP Suite folder", "Click Choose Folder… first.")
            return
        }
        guard let environment = selectedEnvironment else {
            showError("Choose an environment", "Click Find Best Automatically or choose one from the list.")
            return
        }

        UserDefaults.standard.set(suite.path, forKey: "suitePath")
        saveSelectedEnvironment()
        setBusy(true, message: "Checking \(environment.name)…")
        addLog("Checking \(shortPath(environment.folder.path))")

        DispatchQueue.global(qos: .userInitiated).async {
            let result = self.check(environment: environment, suite: suite)
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

    @objc private func findBestEnvironment() {
        guard let suite = selectedSuite, isSuiteFolder(suite) else {
            showError("Choose the NLP Suite folder", "Click Choose Folder… first.")
            return
        }
        guard !environments.isEmpty else {
            showError("No environments found", "Click Rescan or Choose…")
            return
        }

        let likely = environments.filter { $0.name.localizedCaseInsensitiveContains("nlp") }
        let choices = likely.isEmpty ? environments : likely
        setBusy(true, message: "Checking \(choices.count) environments…")
        addLog("Finding the best environment.")

        DispatchQueue.global(qos: .userInitiated).async {
            var best: (Environment, CheckReport)?

            for environment in choices {
                DispatchQueue.main.async {
                    self.statusLabel.stringValue = "Checking \(environment.label)…"
                }

                if case .success(let report) = self.check(environment: environment, suite: suite) {
                    let newScore = report.score(for: self.macArchitecture)
                    let oldScore = best?.1.score(for: self.macArchitecture) ?? -1
                    if newScore > oldScore {
                        best = (environment, report)
                    }
                }
            }

            DispatchQueue.main.async {
                guard let best else {
                    self.setBusy(false, message: "No working environment found.")
                    self.addLog("No environment passed the check.")
                    return
                }

                self.reloadEnvironmentMenu(preferred: best.0.folder)
                self.reports[best.0.folder] = best.1
                self.saveSelectedEnvironment()
                self.showReport(best.1)
                self.addLog("Best choice: \(shortPath(best.0.folder.path))")
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
        let lipo = URL(fileURLWithPath: "/usr/bin/lipo")
        guard let output = try? run(lipo, ["-archs", executable.path]), output.status == 0 else {
            return true
        }
        return output.text.split(whereSeparator: \.isWhitespace).contains { $0 == macArchitecture }
    }

    private func allowMacToOpen(_ suite: URL) {
        let executable = suite.appendingPathComponent("NLP_Suite")
        _ = try? run(
            URL(fileURLWithPath: "/usr/bin/xattr"),
            ["-dr", "com.apple.quarantine", suite.path]
        )
        _ = try? run(
            URL(fileURLWithPath: "/bin/chmod"),
            ["+x", executable.path]
        )
    }

    @objc private func removeExecutableQuarantine() {
        guard let suite = selectedSuite, isSuiteFolder(suite) else {
            showError("Choose the NLP Suite folder", "Click Choose Folder… first.")
            return
        }

        let executable = suite.appendingPathComponent("NLP_Suite")
        let result = try? run(
            URL(fileURLWithPath: "/usr/bin/xattr"),
            ["-r", "-d", "com.apple.quarantine", executable.path]
        )

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

    @objc private func openSuite() {
        guard let suite = selectedSuite, isSuiteFolder(suite) else {
            showError("Choose the NLP Suite folder", "Click Choose Folder… first.")
            return
        }
        guard let environment = selectedEnvironment else {
            showError("Choose an environment", "Click Find Best Automatically first.")
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

        guard let report = reports[environment.folder] else {
            showError("Check the setup first", "Click Check This Setup.")
            return
        }
        guard report.importantChecksPass else {
            showError("This setup is not ready", "Click Find Best Automatically or choose another environment.")
            return
        }
        guard report.architecture == macArchitecture else {
            showError("Wrong environment type", "Choose an environment made for this Mac.")
            return
        }

        allowMacToOpen(suite)

        let logFolder = FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent("Library/Logs")
        try? FileManager.default.createDirectory(at: logFolder, withIntermediateDirectories: true)
        let logFile = logFolder.appendingPathComponent("NLP-Suite-Mac-Setup.log")
        FileManager.default.createFile(atPath: logFile.path, contents: nil)

        do {
            let logHandle = try FileHandle(forWritingTo: logFile)
            try logHandle.seekToEnd()

            let process = Process()
            process.executableURL = suite.appendingPathComponent("NLP_Suite")
            process.currentDirectoryURL = suite
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
