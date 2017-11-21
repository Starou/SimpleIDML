var message = "Available profiles are: ";
for (var i = 0; i < app.pdfExportPresets.count(); i++) {
    var profileName = app.pdfExportPresets[i].name;
    var fullName = app.pdfExportPresets[i].fullName;
    message = message + profileName + " (" + fullName + ") | ";
}
throw message;
