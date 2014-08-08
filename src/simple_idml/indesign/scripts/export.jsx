var src_filename = app.scriptArgs.get("source");
var dst_filename = app.scriptArgs.get("destination");
var format = app.scriptArgs.get("format");
app.open(File(src_filename));

var myDocument = app.documents.item(0);

if (format === "pdf") {
    myDocument.exportFile(ExportFormat.pdfType,
                          new File(dst_filename));
}

app.documents.item(0).close();
