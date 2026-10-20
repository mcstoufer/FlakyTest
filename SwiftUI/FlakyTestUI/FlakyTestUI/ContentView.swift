//
//  SPDX-FileCopyrightText: 2026 Martin Stoufer
//  SPDX-License-Identifier: GPL-3.0-only
//
//  ContentView.swift
//  FlakyTestUI
//
//  Created by Martin Stoufer on 10/19/26.
//

import SwiftUI
import FlakyTest

struct ContentView: View {
    @State private var viewModel = FlakyTestUIViewModel()
    
    var body: some View {
        VStack {
            HStack() {
                if !viewModel.errorString.isEmpty {
                    Text(viewModel.errorString)
                }
                Spacer()
                Stepper("Test Window (\(viewModel.items.count))",
                        value: Binding(
                            get: { viewModel.items.count },
                            set: { newValue in
                                if newValue > viewModel.items.count {
                                    viewModel.addTest()
                                } else {
                                    viewModel.deleteLastTest()
                                }
                            }
                        ),
                        in: FlakyTest.MIN_TEST_COUNT...30)
            }
            HStack(spacing: 12) {
                ForEach(viewModel.items.indices, id: \.self) { index in
                    VStack(spacing: 8) {
                        Text(viewModel.items[index].name)
                            .font(.caption)
                            .fontWeight(.medium)
                        
                        Toggle("", isOn: Binding(
                            get: { viewModel.items[index].isOn},
                            set: { newValue in
                                withAnimation(.snappy) {
                                    viewModel.updateToggleState(at: index, to: newValue)
                                }
                            }
                        ))
                        .labelsHidden()
                        .toggleStyle(CustomColoredVerticalToggleStyle())
                        .padding(4) // Retains your requested 4px safety frame boundary
                    }
                }
            }
           
            HStack() {
                if viewModel.confidence != 0.0 {
                    Text("Confidence level: \(viewModel.confidence, specifier: "%.2f")%")
                }
                Spacer()
                Button("Evaluate") {
                    Task {
                       await viewModel.findConfidence()
                    }
                }
                .frame(alignment: .trailing)
                .padding(.horizontal, 8)
            }
        }
        .padding()
    }
}

#Preview {
    ContentView()
}
