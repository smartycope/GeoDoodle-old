import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.3

Window {
    visible: true
    width: 640
    height: 480
    property alias element3Text: testTextOut.text
    title: qsTr("Hello World")

    Text {
        id: titleText
        x: 282
        y: 22
        text: qsTr("Edit Settings")
        font.pixelSize: 12
    }

    Text {
        id: dotSpreadText
        x: 59
        y: 128
        text: qsTr("Dot Spread")
        renderType: Text.NativeRendering
        font.pixelSize: 12
    }

    MouseArea {
        id: hoverAreaTest
        x: 52
        y: 122
        width: 83
        height: 26
        hoverEnabled: true
    }

    Text {
        id: continueKeyText
        x: 59
        y: 202
        width: 80
        height: 15
        text: qsTr("Continue Key")
        font.pixelSize: 12
    }

    Text {
        id: numEntersText
        x: 59
        y: 251
        text: qsTr("Number of Outlying Points")
        font.pixelSize: 12
    }

    Switch {
        id: continueKeySwitch
        x: 280
        y: 198
        text: qsTr("Space Bar")
        autoExclusive: false
        hoverEnabled: false
        checked: true
        display: AbstractButton.TextOnly
    }

    Text {
        id: cKeyText
        x: 242
        y: 203
        text: qsTr("c key")
        font.pixelSize: 12
    }

    TextField {
        id: numEntersField
        x: 242
        y: 243
        text: qsTr("")
        renderType: Text.NativeRendering
    }

    TextInput {
        id: testTextIn
        x: 280
        y: 327
        width: 80
        height: 21
        text: qsTr("Enter Text Here")
        font.pixelSize: 12
    }

    Text {
        id: testTextOut
        x: 307
        y: 362
        width: 27
        height: 18
        text: qsTr("Text")
        font.pixelSize: 12
    }

    TextField {
        id: dotSpreadField
        x: 242
        y: 120
        text: qsTr("")
        renderType: Text.NativeRendering
    }

    Button {
        id: button
        x: 491
        y: 120
        width: 41
        height: 31
        text: qsTr("")
    }

    Text {
        id: element
        x: 468
        y: 90
        text: qsTr("Align to 1/4 in.")
        font.pixelSize: 12
    }

    CheckBox {
        id: checkBox
        x: 242
        y: 157
        text: qsTr("Measure in mm")
        checked: false
        display: AbstractButton.TextOnly
    }
}
