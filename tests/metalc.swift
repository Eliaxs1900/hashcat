// metalc <source> [NAME=VALUE ...]: build <source> with Metal's runtime compiler, as hashcat does
// (MTLDevice newLibraryWithSource, macros as preprocessorMacros), and print the compiler's errors
// and warnings, or "compiled OK".
import Metal
import Foundation

let args = CommandLine.arguments
let data = FileManager.default.contents(atPath: args[1])!
let src = String(decoding: data, as: UTF8.self)
var macros: [String: NSObject] = [:]
for a in args.dropFirst(2) {
  let kv = a.split(separator: "=", maxSplits: 1).map(String.init)
  macros[kv[0]] = (kv.count > 1 ? kv[1] : "1") as NSString
}
let opts = MTLCompileOptions()
opts.preprocessorMacros = macros
let device = MTLCreateSystemDefaultDevice()!
do {
  _ = try device.makeLibrary(source: src, options: opts)
  print("compiled OK")
} catch {
  let lines = error.localizedDescription.split(separator: "\n")
  let msgs = lines.filter { $0.contains(": error:") || $0.contains(": warning:") }
  for m in msgs { print(m) }
}
