for(myCounter = app.documents.length; myCounter > 0; myCounter--){
  app.documents.item(myCounter-1).close(SaveOptions.no);
}
