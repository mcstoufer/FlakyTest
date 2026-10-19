//
//  Permutations.swift
//  FlakyTest
//
//  Created by Martin Stoufer on 10/17/26.
//
import Foundation
import OSLog

class Permutations {
    static let DOTFILE_PATH = ".flaky_formulary.json"
    
    let window: Int
    var allPermutations: [[String]]
    
    init(window: Int = 0) {
        self.window = window
        self.allPermutations = []
        load(size: window)
    }
    
    func findConfidence(testResult: TestResult, beta: Float=4.0) -> Float {
        let resultTemplate = allPermutations[testResult.failCount]
        let length = resultTemplate.count
        let spread = pow(Float((floor(Float(length/2)))) / 1.3, beta)
        let resultIndex = resultTemplate.firstIndex(of: testResult.string)
        
        let allWeights: [Float] = (0...length).map { index in
            return calculateWeight(index: index, length: length, spread: spread)
        }
        
        return allWeights[resultIndex!]
    }
    
    private func generateAll() {
        (0...Int(ceil(Float(window+1)/2.0))).forEach { passing in
            let failing = window-passing
            let permutations = generatePassFailPermutations(pass: passing, fail: failing)
            updateFormularies(index: passing, permutations: permutations)
            updateFormularies(index: failing, permutations: permutations.invert())
        }
        self.write()
    }
    
    private func updateFormularies(index: Int, permutations: [String]) {
        allPermutations[index] = permutations
    }
    
    private func calculateWeight(index: Int, length: Int, spread: Float, beta:Float=4.0) -> Float {
        let midpoint = (length-1) / 2
        let exponent = pow(Float(abs(index - midpoint)), beta) / spread
        let weight = 100 * exp(-exponent)
        return weight
    }
    
    
    private func generatePassFailPermutations(
        pass: Int,
        fail: Int,
        currentSequence: String = ""
    ) -> [String] {
        
        var allSequences = [String]()
        
        func generate(pass: Int, fail: Int, current: String) {
            if pass == 0 && fail == 0 {
                allSequences.append(currentSequence)
                return
            }
            if pass > 0 { generate(pass: pass-1, fail: fail, current: current+"1") }
            if fail > 0 { generate(pass: pass, fail: fail-1, current: current+"0") }
        }
        
        generate(pass: pass, fail: fail, current: "")
        return allSequences
    }
    
    private func load(size: Int) {
        let homeDirectory = FileManager.default.homeDirectoryForCurrentUser
        let fileURL = homeDirectory.appendingPathComponent(Permutations.DOTFILE_PATH)
        
        if FileManager.default.fileExists(atPath: fileURL.path) {
            do {
                let jsonData = try Data(contentsOf: fileURL)
                allPermutations = try JSONDecoder().decode([[String]].self, from: jsonData)
                if allPermutations.count != self.window+1 {
                    allPermutations = Array(repeating: [], count: window+1)
                    Logger.engine.info("Updating formulary file. This may take a few moments for large windows.")
                    self.generateAll()
                }
            }
            catch {
                Logger.engine.error("Decoding error: \(error)")
            }
        } else {
            allPermutations = Array(repeating: [], count: window+1)
            Logger.engine.info("Did not find formulary file. Will create now.")
            self.generateAll()
        }
    }
    
    private func write() {
        let homeDirectory = FileManager.default.homeDirectoryForCurrentUser
        let fileURL = homeDirectory.appendingPathComponent(Permutations.DOTFILE_PATH)
        do {
            let jsonData = try JSONEncoder().encode(allPermutations)
            try jsonData.write(to: fileURL)
            Logger.engine.info("Formularies file created at: \(fileURL.path)")
        } catch {
            Logger.engine.error("Failed to write Formularies: \(error)")
        }
    }
}
