import { Wallet } from "ethers";

const wallet = Wallet.createRandom();
const message = "Lab1: підпис з ethers.js";
const signature = await wallet.signMessage(message);

console.log("Address:", wallet.address);
console.log("Message:", message);
console.log("Signature:", signature);
