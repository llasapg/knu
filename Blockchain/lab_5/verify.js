import { verifyMessage } from "ethers";

// вставте значення з sign.js
const message = "Lab1: підпис з ethers.js";
const signature = "0x9e6937b239cc7ba8f2f866509310a3639924138ac2a36e62bb3d5a1c01a3f90359a622a30a47a535a51f6c270edfe9e4bc75ee4943fbc93fe08a9cefda7e6aa91b";

const recovered = verifyMessage(message, signature);
console.log("Recovered address:", recovered);
