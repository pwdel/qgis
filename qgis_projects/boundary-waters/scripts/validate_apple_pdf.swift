import PDFKit
import AppKit
let args=CommandLine.arguments
guard let doc=PDFDocument(url:URL(fileURLWithPath:args[1])) else { print("FAILED: Apple PDFKit rejected file"); exit(1) }
print("pages",doc.pageCount)
for i in 0..<doc.pageCount {
 let page=doc.page(at:i)!
 let image=page.thumbnail(of:NSSize(width:1224,height:792),for:.mediaBox)
 let rep=NSBitmapImageRep(data:image.tiffRepresentation!)!
 try rep.representation(using:.png,properties:[:])!.write(to:URL(fileURLWithPath:args[2]+"-\(i+1).png"))
}
