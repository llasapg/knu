using System;
using System.Numerics;
using System.Text;

namespace DiffieHellmanDemo
{
    class Program
    {
        // Головний метод програми: принцип – демонстрація асиметричної системи Діффі-Хеллмана як обміну спільним секретним ключем між двома сторонами (Аліса і Боб) без передачі цього секрету по мережі.
        // Працює по кроках: задаємо p і g, обираємо приватні ключі a і b, обчислюємо відкриті ключі A=g^a mod p і B=g^b mod p, потім обчислюємо спільні секрети S_A=B^a mod p і S_B=A^b mod p і показуємо, що вони однакові.
        // Невеликий приклад: p=23, g=5, a=6, b=15 → A=5^6 mod 23=8, B=5^15 mod 23=19, S_A=19^6 mod 23=2, S_B=8^15 mod 23=2.
        static void Main(string[] args)
        {
            Console.OutputEncoding = Encoding.UTF8;
            Console.InputEncoding = Encoding.UTF8;

            BigInteger p = 23;
            BigInteger g = 5;

            BigInteger privateAlice = 6;
            BigInteger privateBob = 15;

            Console.WriteLine("Асиметрична система Діффі-Хеллмана");
            Console.WriteLine();
            Console.WriteLine($"Спільні параметри системи: p = {p}, g = {g}");
            Console.WriteLine();

            BigInteger publicAlice = DiffieHellmanComputePublicKey(p, g, privateAlice);
            BigInteger publicBob = DiffieHellmanComputePublicKey(p, g, privateBob);

            Console.WriteLine("Крок 1. Приватні ключі сторін (не передаються по мережі):");
            Console.WriteLine($"Приватний ключ Аліси: a = {privateAlice}");
            Console.WriteLine($"Приватний ключ Боба:  b = {privateBob}");
            Console.WriteLine();

            Console.WriteLine("Крок 2. Обчислення відкритих ключів (можуть передаватися по відкритому каналу):");
            Console.WriteLine($"Відкритий ключ Аліси: A = g^a mod p = {publicAlice}");
            Console.WriteLine($"Відкритий ключ Боба:  B = g^b mod p = {publicBob}");
            Console.WriteLine();

            BigInteger sharedAlice = DiffieHellmanComputeSharedKey(p, publicBob, privateAlice);
            BigInteger sharedBob = DiffieHellmanComputeSharedKey(p, publicAlice, privateBob);

            Console.WriteLine("Крок 3. Обчислення спільного секрету кожною стороною:");
            Console.WriteLine($"Спільний секрет Аліси: S_A = B^a mod p = {sharedAlice}");
            Console.WriteLine($"Спільний секрет Боба:  S_B = A^b mod p = {sharedBob}");
            Console.WriteLine();
            Console.WriteLine($"Перевірка: S_A і S_B збігаються: {sharedAlice == sharedBob}");
            Console.WriteLine();

            Console.WriteLine("Додаткова демонстрація: використаємо спільний секрет як ключ для симетричного шифрування одного великого числа.");
            Console.WriteLine($"Спільний секрет S = {sharedAlice}");
            Console.WriteLine("Введіть ціле число для шифрування (можна дуже велике):");

            string input = Console.ReadLine() ?? "123";
            if (!BigInteger.TryParse(input, out BigInteger message))
            {
                message = 123;
            }

            BigInteger encrypted = EncryptWithSharedKey(message, sharedAlice);
            BigInteger decrypted = DecryptWithSharedKey(encrypted, sharedAlice);

            Console.WriteLine();
            Console.WriteLine("Результат симетричного шифрування на основі спільного секрету:");
            Console.WriteLine($"Відкритий текст (число): {message}");
            Console.WriteLine($"Шифртекст (число):       {encrypted}");
            Console.WriteLine($"Розшифрування:           {decrypted}");
            Console.WriteLine();
            Console.WriteLine("Головний акцент: спільний секрет отримано асиметрично (через Діффі-Хеллмана), без передачі його по мережі.");
            Console.WriteLine();
            Console.WriteLine("Натисніть Enter для завершення...");
            Console.ReadLine();
        }

        // Метод обчислення відкритого ключа Діффі-Хеллмана: принцип – відкритий ключ A обчислюється як A = g^a mod p, де p – велике просте число, g – первісний корінь (база), a – приватний ключ.
        // Працює як одностороння функція: легко обчислити A за відомими g, p і a, але важко відновити a тільки з p, g і A (це задача обчислення дискретного логарифма).
        // Приклад: p=23, g=5, a=6 → A=5^6 mod 23=15625 mod 23=8.
        static BigInteger DiffieHellmanComputePublicKey(BigInteger p, BigInteger g, BigInteger privateKey)
        {
            return BigInteger.ModPow(g, privateKey, p);
        }

        // Метод обчислення спільного секрету Діффі-Хеллмана: принцип – кожна сторона підносить відкритий ключ іншої сторони до ступеня свого приватного ключа за модулем p: S = (publicOther^privateSelf) mod p.
        // Працює так, що обидві сторони отримують однаковий результат, бо g^(ab) mod p = g^(ba) mod p. Секрет S ніколи не передається по мережі, передаються тільки p, g, A і B.
        // Приклад: p=23, A=8, B=19, a=6, b=15 → S_A=19^6 mod 23=2, S_B=8^15 mod 23=2.
        static BigInteger DiffieHellmanComputeSharedKey(BigInteger p, BigInteger publicOther, BigInteger privateSelf)
        {
            return BigInteger.ModPow(publicOther, privateSelf, p);
        }

        // Метод шифрування числа на основі спільного секрету: принцип – шифртекст C отримуємо як C = M + S, де M – відкрите число, S – спільний секрет.
        // Працює як простий симетричний шифр "зсувом" у просторі цілих чисел, де роль ключа виконує спільний секрет, отриманий через Діффі-Хеллмана.
        // Приклад: M=1000, S=42 → C=1042.
        static BigInteger EncryptWithSharedKey(BigInteger value, BigInteger sharedKey)
        {
            return value + sharedKey;
        }

        // Метод дешифрування числа на основі спільного секрету: принцип – розшифрування виконується як M = C - S, де C – шифртекст, S – той самий спільний секрет.
        // Працює, бо обидві сторони мають один і той самий S, тому можуть виконати обернену операцію додавання і відновити початкове число.
        // Приклад: C=1042, S=42 → M=1000.
        static BigInteger DecryptWithSharedKey(BigInteger value, BigInteger sharedKey)
        {
            return value - sharedKey;
        }
    }
}