var src_filename = app.scriptArgs.get("source");
var dst_filename = app.scriptArgs.get("destination");
app.open(File(src_filename));

var myDocument = app.documents.item(0);
myDocument.save(new File(dst_filename));

app.documents.item(0).close();
