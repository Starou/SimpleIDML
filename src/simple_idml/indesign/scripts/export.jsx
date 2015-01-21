/* Export In various formats */
var SAMPLING = {
    'subSample': Sampling.SUBSAMPLE,
    'downSample': Sampling.DOWNSAMPLE,
    'bicubicDownSample': Sampling.BICUBIC_DOWNSAMPLE
};

var BMP_QUALITY = {
    'minimum': CompressionQuality.MINIMUM,
    'low': CompressionQuality.LOW,
    'medium': CompressionQuality.MEDIUM,
    'high': CompressionQuality.HIGH,
    'maximum': CompressionQuality.MAXIMUM,
    '4bits': CompressionQuality.FOUR_BIT,
    '8bits': CompressionQuality.EIGHT_BIT
};

var BMP_COMPRESSION = {
    'auto': BitmapCompression.AUTO_COMPRESSION,
    'jpeg': BitmapCompression.JPEG,
    'zip': BitmapCompression.ZIP,
    'jpeg2000': BitmapCompression.JPEG_2000,
    'autoJpeg2000': BitmapCompression.AUTOMATIC_JPEG_2000
};

var MONO_COMPRESSION = {
    'CCIT3': MonoBitmapCompression.CCIT3,
    'CCIT4': MonoBitmapCompression.CCIT4,
    'zip': MonoBitmapCompression.ZIP,
    'RLE': MonoBitmapCompression.RUN_LENGTH
};

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

// Update out-of-date links.
for (var i = 0; i < myDocument.links.count(); i++) {
    var link = myDocument.links.item(i);
    if (link.status === LinkStatus.LINK_OUT_OF_DATE) {
        link.update();
    }
}

if (format === "pdf") {
    var pdfExportPresetName = app.scriptArgs.get("pdfExportPresetName");
    // Use an export preset.
    if (pdfExportPresetName !== "") {
        myDocument.exportFile(ExportFormat.pdfType, new File(dst_filename),
                              app.pdfExportPresets.item(pdfExportPresetName));
    }
    // Or parameters.
    else {
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

        var _colorBitmapSampling = app.scriptArgs.get("colorBitmapSampling") ? SAMPLING[app.scriptArgs.get("colorBitmapSampling")] : Sampling.NONE;
        var _colorBitmapQuality = app.scriptArgs.get("colorBitmapQuality") ? BMP_QUALITY[app.scriptArgs.get("colorBitmapQuality")] : CompressionQuality.HIGH;
        var _colorBitmapCompression = app.scriptArgs.get("colorBitmapCompression") ? BMP_COMPRESSION[app.scriptArgs.get("colorBitmapCompression")] : BitmapCompression.NONE;
        var _colorBitmapSamplingDPI = parseInt(app.scriptArgs.get("colorBitmapSamplingDPI")) || 150;

        var _grayscaleBitmapSampling = app.scriptArgs.get("grayscaleBitmapSampling") ? SAMPLING[app.scriptArgs.get("grayscaleBitmapSampling")] : Sampling.NONE;
        var _grayscaleBitmapQuality = app.scriptArgs.get("grayscaleBitmapQuality") ? BMP_QUALITY[app.scriptArgs.get("grayscaleBitmapQuality")] : CompressionQuality.HIGH;
        var _grayscaleBitmapCompression = app.scriptArgs.get("grayscaleBitmapCompression") ? BMP_COMPRESSION[app.scriptArgs.get("grayscaleBitmapCompression")] : BitmapCompression.NONE;
        var _grayscaleBitmapSamplingDPI = parseInt(app.scriptArgs.get("grayscaleBitmapSamplingDPI")) || 150;

        var _monochromeBitmapSampling = app.scriptArgs.get("monochromeBitmapSampling") ? SAMPLING[app.scriptArgs.get("monochromeBitmapSampling")] : Sampling.NONE;
        var _monochromeBitmapCompression = app.scriptArgs.get("monochromeBitmapCompression") ? MONO_COMPRESSION[app.scriptArgs.get("monochromeBitmapCompression")] : MonoBitmapCompression.NONE;
        var _monochromeBitmapSamplingDPI = parseInt(app.scriptArgs.get("monochromeBitmapSamplingDPI")) || 600;

        var bleeds = {
            top:  parseFloat(app.scriptArgs.get("bleedTop")) || 0,
            bottom: parseFloat(app.scriptArgs.get("bleedBottom")) || 0,
            inside: parseFloat(app.scriptArgs.get("bleedInside")) || 0,
            outside: parseFloat(app.scriptArgs.get("bleedOutside")) || 0
        };
        var _pageMarksOffset = parseInt(app.scriptArgs.get("pageMarksOffset")) || 12;

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
            colorBitmapCompression = _colorBitmapCompression;
            colorBitmapQuality = _colorBitmapQuality;
            colorBitmapSampling = _colorBitmapSampling;
            if (colorBitmapSampling != Sampling.NONE) {
                colorBitmapSamplingDPI = _colorBitmapSamplingDPI;
                thresholdToCompressColor = colorBitmapSamplingDPI * 1.5;
            }
            grayscaleBitmapCompression = _grayscaleBitmapCompression;
            grayscaleBitmapQuality = _grayscaleBitmapQuality;
            grayscaleBitmapSampling = _grayscaleBitmapSampling;
            if (grayscaleBitmapSampling != Sampling.NONE) {
                grayscaleBitmapSamplingDPI = _grayscaleBitmapSamplingDPI;
                thresholdToCompressGray = grayscaleBitmapSamplingDPI * 1.5;
            }
            monochromeBitmapCompression = _monochromeBitmapCompression;
            monochromeBitmapSampling = _monochromeBitmapSampling;
            if (monochromeBitmapSampling != Sampling.NONE) {
                monochromeBitmapSamplingDPI = _monochromeBitmapSamplingDPI;
                thresholdToCompressMonochrome = monochromeBitmapSamplingDPI * 1.5;
            }
            //
            //Other compression options.
            compressionType = PDFCompressionType.compressNone;
            compressTextAndLineArt = true;
            cropImagesToFrames = true;
            optimizePDF = _optimizePDF;
            //
            //Printers marks and prepress options.
            //Get the bleed amounts from the document's bleed.
            bleedBottom = bleeds.bottom;
            bleedTop = bleeds.top;
            bleedInside = bleeds.inside;
            bleedOutside = bleeds.outside;
            //If any bleed area is greater than zero, then export the bleed marks.
            useDocumentBleedWithPDF = false;
            if (bleedBottom === 0 && bleedTop === 0 && bleedInside === 0 && bleedOutside === 0){
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
            pageMarksOffset = _pageMarksOffset;
            pdfMarkType = MarkTypes.DEFAULT_VALUE;
            printerMarkWeight = PDFMarkWeight.p125pt;
            registrationMarks = _registrationMarks;
            try {
                simulateOverprint = false;
            }
            catch(e){}
            //Set viewPDF to true to open the PDF in Acrobat or Adobe Reader.
            viewPDF = false;
            //
            // Output
            pdfColorSpace = _colorSpace;
            pdfDestinationProfile = _colorProfile;
            pdfXProfile = _colorProfile;
            //
            // Advanced
            appliedFlattenerPreset = app.flattenerPresets.itemByName(_flattenerPresetName);
        }
        myDocument.exportFile(ExportFormat.pdfType, new File(dst_filename));
    }
} else if (format === "jpeg") {
    myDocument.exportFile(ExportFormat.JPG, new File(dst_filename));
} else if (format === "idml") {
    myDocument.exportFile(ExportFormat.INDESIGN_MARKUP, new File(dst_filename));
}

app.documents.item(0).close();
