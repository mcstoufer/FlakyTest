# flaky-test

Evaluate flaky test histories using weighted distribution measurements Distributed as lightweight packages or libraries, this will provide you with an easy way to identify the "flakiness" level of a given set of past test results. 

There are two parts of this Project:
* [Swift / SwiftUI](SWIFT.md)
* [Python](PYTHON.md)

### Whats Going On Here
There are few levels here of filtering to allow your calculations to be more concise and give you better feedback when evaluating large sets of test results.

#### Test definition
Uniquely identified by its Module/Class/TestName/TestContent. This is up to you to properly assemble for your needs. Just ensure there is an absolutely unique hash for each test you're tracking. If the content for a given test changes. It is a different test now and should be tracked accordingly.

#### Results filtering
Now that you have a large set of test results recorded somewhere, you can make an initial cut of which tests aren't even worth generating a confidence value for. If you have 1 failed run with 24 passes after that, it probably isn't worth your effort to dig into now, if ever. Conversely, if you have 24 failures with only 1 passing test, that test isn't flaky; it's broken and should be addressed first.

Setting the Fail Percent Lower and Upper values to the FlakyTest class initialization will configure these bounds for you. They default to .10 and .85 respectively.

#### Deviation bounding
The logic implementation  here sets a nominal standard deviation value of 4.0 as its default value. This gives good response and does a balanced job of measuring the flaky confidence value. Moving it up starts to isolate the real flaky tests and moving it lower allows more tests to report high confidence values. Set this to meet your filtering needs.

Licensed under the [GNU General Public License v3.0 only](LICENSE)
(`SPDX-License-Identifier: GPL-3.0-only`).

