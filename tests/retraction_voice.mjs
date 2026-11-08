// Only publisher quotation nodes explicitly marked by the renderer are quotations.
// Keep the earlier publisher-title marker compatible with already rendered title fragments.
// Strip other tags while preserving their text: a link is not an attribution boundary.
export function scanVoice(html) {
  const voice = String(html)
    .replace(/<span data-publisher-(?:quote|title)>[\s\S]*?<\/span>/gi, "")
    .replace(/<[^>]*>/g, "");
  return ["fraud", "fake", "fabricat", "deceiv", "cheat", "discredit", "misconduct", "liar"]
    .filter(word => new RegExp(word, "i").test(voice));
}
