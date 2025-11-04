if (typeof window.okxwallet !== 'undefined') {
    console.log('OKX Wallet встановлений!');
    // Запит доступу до акаунтів
    window.okxwallet.request({ method: 'eth_requestAccounts' })
        .then((accounts) => {
            console.log('✅ Підключення успішне! Аккаунти:', accounts);
        })
        .catch((err) => {
            console.error('❌ Помилка підключення до OKX Wallet:', err);
        });
} else {
    alert('Встановіть OKX Wallet!');
}

// Створення екземпляра web3
const web3 = new Web3(window.okxwallet);

// Адреса контракту та ABI
const contractAddress = '0xA087e0A9E37F19E13d976D40dc3D1f4b42dED90a';
const contractABI = [
    {
        "inputs": [],
        "name": "get",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "x",
                "type": "uint256"
            }
        ],
        "name": "set",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "storedData",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
];

// Підключення до контракту
const contract = new web3.eth.Contract(contractABI, contractAddress);

// Функція для запису числа
async function setData() {
    const inputData = document.getElementById('inputData').value;
    const accounts = await web3.eth.getAccounts();
    console.log('🔹 Виклик set() від аккаунта:', accounts[0]);
    await contract.methods.set(inputData).send({ from: accounts[0] });
    console.log('✅ Транзакція set() успішно відправлена');
}

// Функція для отримання числа
async function getData() {
    console.log('🔹 Виклик get()...');
    const result = await contract.methods.get().call();
    console.log('✅ Отримано значення з контракту:', result);
    document.getElementById('displayData').innerText = result;
}