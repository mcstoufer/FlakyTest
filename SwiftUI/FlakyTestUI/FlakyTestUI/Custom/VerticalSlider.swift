//
//  SPDX-FileCopyrightText: 2026 Martin Stoufer
//  SPDX-License-Identifier: GPL-3.0-only
//
//  VerticalSlider.swift
//  FlakyTestUI
//
//  Created by Martin Stoufer on 10/21/26.
//

import SwiftUI
import FlakyTest

struct VerticalSlider: View {
    @Binding var value: Float
    
    var bounds: ClosedRange<Float> = Float(FlakyTest.DEFAULT_DEV_BOUND)-1.0...Float(FlakyTest.DEFAULT_DEV_BOUND)+1.0
    
    var body: some View {
        // 1. Use an invisible layout anchor that expands vertically to fill the parent space
        Rectangle()
            .fill(Color.clear)
            .frame(width: 32) // Acts as the explicit horizontal hitbox width for the slider
            .frame(maxHeight: .infinity)
            .overlay {
                // 2. Read the actual parent height allocated to the layout anchor
                GeometryReader { proxy in
                    Slider(value: $value, in: bounds)
                    // 3. Force the slider's horizontal width to match the parent's actual height
                        .frame(width: proxy.size.height)
                        .rotationEffect(.degrees(-90))
                    // 4. Center the rotated slider over the layout anchor box
                        .offset(
                            x: (proxy.size.width - proxy.size.height) / 2,
                            y: (proxy.size.height - proxy.size.width) / 2
                        )
                }
            }
    }
}
