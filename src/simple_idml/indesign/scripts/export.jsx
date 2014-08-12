var src_filename = app.scriptArgs.get("source");
var dst_filename = app.scriptArgs.get("destination");
var format = app.scriptArgs.get("format");
app.open(File(src_filename));

var myDocument = app.documents.item(0);

if (format === "pdf") {
    myDocument.exportFile(ExportFormat.pdfType,
                          new File(dst_filename));
} else if (format === "jpeg") {
    myDocument.exportFile(ExportFormat.JPG,
                          new File(dst_filename));
} else if (format === "idml") {
    myDocument.exportFile(ExportFormat.INDESIGN_MARKUP,
                          new File(dst_filename));
}

app.documents.item(0).close();
