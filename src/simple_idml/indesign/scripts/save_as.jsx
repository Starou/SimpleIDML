if (!app.scriptArgs.isDefined("source")) {
    var src_file = File.openDialog("Choose the source file");
    var dst_file = File.saveDialog("Choose the destination file");
} else {
    var src_file = new File(app.scriptArgs.get("source"));
    var dst_file = new File(app.scriptArgs.get("destination"));
}

app.open(src_file);
var myDocument = app.documents.item(0);

// Update out-of-date links.
for (var i = 0; i < myDocument.links.count(); i++) {
    var link = myDocument.links.item(i);
    if (link.status === LinkStatus.LINK_OUT_OF_DATE) {
        link.update();
    }
}

myDocument.save(dst_file);
app.documents.item(0).close();
