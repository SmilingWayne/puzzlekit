export class PzkError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "PzkError";
  }
}
