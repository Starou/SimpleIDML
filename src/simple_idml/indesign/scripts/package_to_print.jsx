// http://www.indd-skript.de/extendscriptAPI/indesign10/#Document.html#d1e47196__d1e49964

function createPackage(dir, doc, params){
     myDocument.packageForPrint(dir, 
         params.copyingFonts, 
         params.copyingLinkedGraphics, 
         params.copyingProfiles, 
         params.updatingGraphics, 
         params.includingHiddenLayers,
         params.ignorePreflightErrors, 
         params.creatingReport, 
         params.includeIDML,  // Those 3 parameters are for CC 2014.
         params.includePDF,
         params.PDFStyle,
         params.versionComments,
         params.forceSave);
}

var src_filename = app.scriptArgs.get("source");
var dst_dir = app.scriptArgs.get("destination");
app.open(File(src_filename));
var params = {
     copyingFonts: true,
     copyingLinkedGraphics: true,
     copyingProfiles: true,
     updatingGraphics: true,
     includingHiddenLayers: false,
     ignorePreflightErrors: true,
     creatingReport: true,
     includeIDML: false,
     includePDF: false,
     PDFStyle: "",
     versionComments: "",
     forceSave: false
};

var myDocument = app.documents.item(0);

createPackage(dst_dir, myDocument, params);
myDocument.close();
