// From https://forums.adobe.com/thread/729156.
// InDesignSDK5_5/docs/references/scripting-dom-javascript-CS5.5.html#kPackageMethodScriptElement

function createPackage(dir, doc, params){
     myDocument.packageForPrint(dir, 
         params.copyingFonts, 
         params.copyingLinkedGraphics, 
         params.copyingProfiles, 
         params.updatingGraphics, 
         params.includingHiddenLayers,
         params.ignorePreflightErrors, 
         params.creatingReport, 
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
     versionComments: "",
     forceSave: false
};

var myDocument = app.documents.item(0);

createPackage(dst_dir, myDocument, params)
