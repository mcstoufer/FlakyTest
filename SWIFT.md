Both a Swift Library and SwiftUI demo app are provided here. You can either link the library in your own code base via SPM, or use the code directly and maintain the GPLv3 license link.

For the SwiftUI app, just open its project and build. From there you can set your pass/fail values and then evaluate the measured result. This is Swift-6 concurrency based, so we are using Actor and Task here to keep the UI unblocked. Review the organization here to understand how this can be lifted into your own UI project.

![Demo App Screenshot][Resources/AppShot.png]

Adjusting the Pass/Fail Percentage will limit the outliers to help eliminate checking for obvious passing or failing test results.

The standard deviation value can also be adjusted to better restrict high confidence values to those results that are truly flaky.