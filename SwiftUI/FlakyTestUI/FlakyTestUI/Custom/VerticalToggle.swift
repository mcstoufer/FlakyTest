//
//  SPDX-FileCopyrightText: 2026 Martin Stoufer
//  SPDX-License-Identifier: GPL-3.0-only
//
//  VerticalToggle.swift
//  FlakyTestUI
//
//  Created by Martin Stoufer on 10/19/26.
//

import SwiftUI

struct CustomColoredVerticalToggleStyle: ToggleStyle {
    func makeBody(configuration: Configuration) -> some View {
        Button {
            withAnimation(.snappy(duration: 0.2)) {
                configuration.isOn.toggle()
            }
        } label: {
            ZStack(alignment: configuration.isOn ? .top : .bottom) {
                Capsule()
                    .fill(configuration.isOn ? Color.red : Color.green)
                    .frame(width: 32, height: 51)
                
                Circle()
                    .fill(Color.white)
                    .padding(2)
                    .frame(width: 28, height: 28)
            }
        }
        .buttonStyle(.plain) // Prevents standard button flash or highlight effects
    }
}
