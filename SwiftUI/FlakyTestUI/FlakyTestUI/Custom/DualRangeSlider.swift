//
//  SPDX-FileCopyrightText: 2026 Martin Stoufer
//  SPDX-License-Identifier: GPL-3.0-only
//
//  DualRangeSlider.swift
//  FlakyTestUI
//
//  Created by Martin Stoufer on 10/21/26.
//

import SwiftUI

struct DualRangeSlider: View {
    @Binding var passPct: Int
    @Binding var failPct: Int
    
    let range: ClosedRange<Int> = 0...100
    let step: Int = 1 // Enforces integer steps
    
    // Style settings
    var trackColor: Color = Color.secondary.opacity(0.3)
    var selectedColor: Color = Color.accentColor
    var handleColor: Color = .white
    var handleSize: CGFloat = 28
    
    var body: some View {
        GeometryReader { geometry in
            let totalWidth = geometry.size.width - handleSize
            
            // Percentage-based positions relative to the bounds
            let totalRange = Double(range.upperBound - range.lowerBound)
            let lowPercent = Double(passPct - range.lowerBound) / totalRange
            let highPercent = Double(failPct - range.lowerBound) / totalRange
            
            // Map percentages to actual coordinate positions
            let lowX = CGFloat(lowPercent) * totalWidth
            let highX = CGFloat(highPercent) * totalWidth
            
            ZStack(alignment: .leading) {
                // Background Track
                Capsule()
                    .fill(trackColor)
                    .frame(height: 6)
                
                // Highlighted Selected Range Track
                Capsule()
                    .fill(selectedColor)
                    .frame(width: highX - lowX, height: 6)
                    .offset(x: lowX + (handleSize / 2))
                
                // Lower Value Thumb Control
                Circle()
                    .fill(handleColor)
                    .frame(width: handleSize, height: handleSize)
                    .shadow(radius: 3)
                    .overlay(
                        Text("\(passPct)")
                            .font(.system(size: 10, weight: .bold, design: .rounded))
                            .foregroundColor(.black)
                            .minimumScaleFactor(0.7) // Ensures 3-digit values downscale to fit
                            .lineLimit(1)
                    )
                    .offset(x: lowX)
                    .gesture(
                        DragGesture()
                            .onChanged { value in
                                // Calculate the absolute location relative to the container geometry bounds
                                let proposedX = value.location.x - (handleSize / 2)
                                let boundedX = min(max(0, proposedX), highX)
                                let percentage = Double(boundedX / totalWidth)
                                
                                let rawValue = Double(range.lowerBound) + percentage * totalRange
                                let steppedValue = round(rawValue / Double(step)) * Double(step)
                                
                                passPct = min(Int(steppedValue), failPct)
                            }
                    )
                
                // Upper Value Thumb Control
                Circle()
                    .fill(handleColor)
                    .frame(width: handleSize, height: handleSize)
                    .shadow(radius: 3)
                    .overlay(
                        Text("\(failPct)")
                            .font(.system(size: 10, weight: .bold, design: .rounded))
                            .foregroundColor(.black)
                            .minimumScaleFactor(0.7) // Ensures 3-digit values downscale to fit
                            .lineLimit(1)
                    )
                    .offset(x: highX)
                    .gesture(
                        DragGesture()
                            .onChanged { value in
                                // Calculate the absolute location relative to the container geometry bounds
                                let proposedX = value.location.x - (handleSize / 2)
                                let boundedX = min(max(lowX, proposedX), totalWidth)
                                let percentage = Double(boundedX / totalWidth)
                                
                                let rawValue = Double(range.lowerBound) + percentage * totalRange
                                let steppedValue = round(rawValue / Double(step)) * Double(step)
                                
                                failPct = max(Int(steppedValue), passPct)
                            }
                    )
            }
            .frame(maxHeight: .infinity)
        }
        .frame(height: handleSize)
    }
}

#Preview {
    @Previewable @State var passPct = 10
    @Previewable @State var failPct = 85
    
    DualRangeSlider(passPct: $passPct, failPct: $failPct)
}
