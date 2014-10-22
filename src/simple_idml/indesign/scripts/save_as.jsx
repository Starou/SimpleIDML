if (!app.scriptArgs.isDefined("source")) {
    var src_file = File.openDialog("Choose the source file");
    var dst_file = File.saveDialog("Choose the destination file");
} else {
    var src_file = new File(app.scriptArgs.get("source"));
    var dst_file = new File(app.scriptArgs.get("destination"));
}

app.open(src_file, false);
var myDocument = app.documents.item(0);
myDocument.save(dst_file);
app.documents.item(0).close();
