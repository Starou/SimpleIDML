var filename = app.scriptArgs.get("source");
var indd_filename = app.scriptArgs.get("destination");
app.open(File(filename));

var myDocument = app.documents.item(0);
myDocument.save(new File(indd_filename));

app.documents.item(0).close();
