import XCTest

final class ReaderUITests: XCTestCase {
    func testFreeVocabularyLoadsThroughNativeBridge() throws {
        let app = XCUIApplication()
        app.launch()
        let link = app.buttons["reader-N5-vocab"]
        XCTAssertTrue(link.waitForExistence(timeout: 15), app.debugDescription)
        link.tap()
        XCTAssertTrue(app.webViews.firstMatch.waitForExistence(timeout: 15))
        let word = app.webViews.staticTexts["私"].firstMatch
        XCTAssertTrue(word.waitForExistence(timeout: 20), app.debugDescription)
        let attachment = XCTAttachment(screenshot: app.screenshot())
        attachment.name = "N5-Vocabulary-iPhone"; attachment.lifetime = .keepAlways; add(attachment)
    }
    func testFreeKanjiLoadsThroughNativeBridge() throws {
        let app = XCUIApplication()
        app.launch()
        let link = app.buttons["reader-N5-kanji"]
        XCTAssertTrue(link.waitForExistence(timeout: 15), app.debugDescription)
        link.tap()
        XCTAssertTrue(app.webViews.firstMatch.waitForExistence(timeout: 15))
        let character = app.webViews.staticTexts["山"].firstMatch
        XCTAssertTrue(character.waitForExistence(timeout: 20), app.debugDescription)
        character.tap()
        let board = app.webViews.descendants(matching: .any).matching(identifier: "কানজি হাতে লেখার বোর্ড").firstMatch
        XCTAssertTrue(board.waitForExistence(timeout: 15), app.debugDescription)
        let attachment = XCTAttachment(screenshot: app.screenshot())
        attachment.name = "N5-Kanji-iPhone"; attachment.lifetime = .keepAlways; add(attachment)
    }
}
