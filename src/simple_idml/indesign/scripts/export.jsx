/* Export In various formats */

var COLOR_SPACES = {
    'CMYK': PDFColorSpace.CMYK,
    'iGry': PDFColorSpace.GRAY,
    'rCMY': PDFColorSpace.REPURPOSE_CMYK,
    'rRGB': PDFColorSpace.REPURPOSE_RGB,
    'cRGB': PDFColorSpace.RGB,
    'unFc': PDFColorSpace.UNCHANGED_COLOR_SPACE
};

var ACROBAT_COMPAT = {
    '4': AcrobatCompatibility.ACROBAT_4,
    '5': AcrobatCompatibility.ACROBAT_5,
    '6': AcrobatCompatibility.ACROBAT_6,
    '7': AcrobatCompatibility.ACROBAT_7,
    '8': AcrobatCompatibility.ACROBAT_8
};

PDFX_STANDARDS = {
    '1A2001': PDFXStandards.PDFX1A2001_STANDARD,
    '1A2003': PDFXStandards.PDFX1A2003_STANDARD,
    '32002': PDFXStandards.PDFX32002_STANDARD,
    '32003': PDFXStandards.PDFX32003_STANDARD,
    '42010': PDFXStandards.PDFX42010_STANDARD
};

if (!app.scriptArgs.isDefined("source")) {
    var src_filename = File.openDialog("Choose the source file");
    var dst_filename = File.saveDialog("Choose the destination file");
    var format = "pdf";
} else {
    var src_filename = new File(app.scriptArgs.get("source"));
    var dst_filename = new File(app.scriptArgs.get("destination"));
    var format = app.scriptArgs.get("format");
}

app.open(File(src_filename));
var myDocument = app.documents.item(0);

if (format === "pdf") {
    var _colorBars = app.scriptArgs.get("colorBars") ? true : false;
    var _cropMarks = app.scriptArgs.get("cropMarks") ? true : false;
    var _optimizePDF = app.scriptArgs.get("optimizePDF") ? true : false;
    var _pageInformationMarks = app.scriptArgs.get("pageInformationMarks") ? true : false;
    var _registrationMarks = app.scriptArgs.get("registrationMarks") ? true : false;

    var _acrobatCompatibility = app.scriptArgs.get("acrobatCompatibility") ? ACROBAT_COMPAT[app.scriptArgs.get("acrobatCompatibility")] : AcrobatCompatibility.ACROBAT_4;
    var _colorSpace = app.scriptArgs.get("colorSpace") ? COLOR_SPACES[app.scriptArgs.get("colorSpace")] : PDFColorSpace.UNCHANGED_COLOR_SPACE;
    var _colorProfile = app.scriptArgs.get("colorProfile") || PDFProfileSelector.USE_NO_PROFILE;
    var _flattenerPresetName = app.scriptArgs.get("flattenerPresetName") || app.flattenerPresets.firstItem().name;
    var _standartsCompliance = app.scriptArgs.get("standartsCompliance") ? PDFX_STANDARDS[app.scriptArgs.get("standartsCompliance")] : PDFXStandards.NONE;


    with(app.pdfExportPreferences){
        //Basic PDF output options.
        pageRange = PageRange.allPages;
        acrobatCompatibility = _acrobatCompatibility;
        standartsCompliance = _standartsCompliance;
        exportGuidesAndGrids = false;
        exportLayers = false;
        exportNonPrintingObjects = false;
        exportReaderSpreads = false;
        generateThumbnails = false;
        try{
            ignoreSpreadOverrides = false;
        }
        catch(e){}
        includeBookmarks = true;
        includeHyperlinks = true;
        includeICCProfiles = true;
        includeSlugWithPDF = false;
        includeStructure = false;
        interactiveElementsOption = InteractiveElementsOptions.doNotInclude;
        //Setting subsetFontsBelow to zero disallows font subsetting;
        //set subsetFontsBelow to some other value to use font subsetting.
        subsetFontsBelow = 0;
        //
        //Bitmap compression/sampling/quality options.
        colorBitmapCompression = BitmapCompression.zip;
        colorBitmapQuality = CompressionQuality.eightBit;
        colorBitmapSampling = Sampling.none;
        //thresholdToCompressColor is not needed in this example.
        //colorBitmapSamplingDPI is not needed when colorBitmapSampling
        //is set to none.
        grayscaleBitmapCompression = BitmapCompression.zip;
        grayscaleBitmapQuality = CompressionQuality.eightBit;
        grayscaleBitmapSampling = Sampling.none;
        //thresholdToCompressGray is not needed in this example.
        //grayscaleBitmapSamplingDPI is not needed when grayscaleBitmapSampling
        //is set to none.
        monochromeBitmapCompression = BitmapCompression.zip;
        monochromeBitmapSampling = Sampling.none;
        //thresholdToCompressMonochrome is not needed in this example.
        //monochromeBitmapSamplingDPI is not needed when
        //monochromeBitmapSampling is set to none.
        //
        //Other compression options.
        compressionType = PDFCompressionType.compressNone;
        compressTextAndLineArt = true;
        cropImagesToFrames = true;
        optimizePDF = _optimizePDF;
        //
        //Printers marks and prepress options.
        //Get the bleed amounts from the document's bleed.
        bleedBottom = 0; // app.activeDocument.documentPreferences.documentBleedBottomOffset;
        bleedTop = 0; //app.activeDocument.documentPreferences.documentBleedTopOffset;
        bleedInside = 0; //app.activeDocument.documentPreferences.documentBleedInsideOrLeftOffset;
        bleedOutside = 0; //app.activeDocument.documentPreferences.documentBleedOutsideOrRightOffset;
        //If any bleed area is greater than zero, then export the bleed marks.
        if (bleedBottom == 0 && bleedTop == 0 && bleedInside == 0 && bleedOutside == 0){
            bleedMarks = true;
        } else {
            bleedMarks = false;
        }
        colorBars = _colorBars;
        colorTileSize = 128;
        grayTileSize = 128;
        cropMarks = _cropMarks;
        omitBitmaps = false;
        omitEPS = false;
        omitPDF = false;
        pageInformationMarks = _pageInformationMarks;
        pageMarksOffset = 12;
        pdfMarkType = MarkTypes.DEFAULT_VALUE;
        printerMarkWeight = PDFMarkWeight.p125pt;
        registrationMarks = _registrationMarks;
        try {
            simulateOverprint = false;
        }
        catch(e){}
        useDocumentBleedWithPDF = true;
        //Set viewPDF to true to open the PDF in Acrobat or Adobe Reader.
        viewPDF = false;
        //
        // Output
        //pdfColorSpace = PDFColorSpace.unchangedColorSpace; //Default mark type.
        pdfColorSpace = _colorSpace; //PDFColorSpace.CMYK;
        pdfDestinationProfile = _colorProfile;
        pdfXProfile = _colorProfile;
        //
        // Advanced
        appliedFlattenerPreset = app.flattenerPresets.itemByName(_flattenerPresetName);
    }
    myDocument.exportFile(ExportFormat.pdfType, new File(dst_filename));
} else if (format === "jpeg") {
    myDocument.exportFile(ExportFormat.JPG, new File(dst_filename));
} else if (format === "idml") {
    myDocument.exportFile(ExportFormat.INDESIGN_MARKUP, new File(dst_filename));
}

app.documents.item(0).close();

