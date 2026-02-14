using System;
using System.Text;

namespace CryptoLab
{
    class Program
    {
        static void Main(string[] args)
        {
            string alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

            Console.OutputEncoding = Encoding.UTF8;
            Console.InputEncoding = Encoding.UTF8;

            Console.WriteLine("Введіть відкритий текст (латинські літери):");
            string plaintext = Console.ReadLine() ?? "";
            plaintext = plaintext.ToUpper();

            Console.WriteLine();
            Console.WriteLine("=== Афінний шифр ===");
            int a = 5;
            int b = 8;
            string affineEncrypted = AffineEncrypt(plaintext, a, b, alphabet);
            string affineDecrypted = AffineDecrypt(affineEncrypted, a, b, alphabet);
            Console.WriteLine($"Ключі: a={a}, b={b} Взаємно прості!");
            Console.WriteLine($"Шифртекст:   {affineEncrypted}");
            Console.WriteLine($"Розшифрування: {affineDecrypted}");

            Console.WriteLine();
            Console.WriteLine("=== Шифр Віженера ===");
            Console.WriteLine("Введіть ключ Віженера (слово латинськими літерами):");
            string vigenereKey = Console.ReadLine() ?? "KEY";
            vigenereKey = vigenereKey.ToUpper();
            string vigenereEncrypted = VigenereEncrypt(plaintext, vigenereKey, alphabet);
            string vigenereDecrypted = VigenereDecrypt(vigenereEncrypted, vigenereKey, alphabet);
            Console.WriteLine($"Ключ: {vigenereKey}");
            Console.WriteLine($"Шифртекст:   {vigenereEncrypted}");
            Console.WriteLine($"Розшифрування: {vigenereDecrypted}");

            Console.WriteLine();
            Console.WriteLine("=== Накладання двійкової гами (XOR) ===");
            Console.WriteLine("Введіть бітовий відкритий текст (рядок з 0 та 1):");
            string bitsPlain = Console.ReadLine() ?? "101010";
            Console.WriteLine("Введіть двійкову гамму (рядок з 0 та 1):");
            string gamma = Console.ReadLine() ?? "1100";
            string bitsEncrypted = GammaBinaryEncrypt(bitsPlain, gamma);
            string bitsDecrypted = GammaBinaryEncrypt(bitsEncrypted, gamma);
            Console.WriteLine($"Відкритий текст: {bitsPlain}");
            Console.WriteLine($"Гамма:           {gamma}");
            Console.WriteLine($"Шифртекст:       {bitsEncrypted}");
            Console.WriteLine($"Розшифрування:   {bitsDecrypted}");

            Console.WriteLine();
            Console.WriteLine("=== Комбінований шифр Френдберга ===");
            Console.WriteLine("Введіть ціле число як ключ (зерно генератора):");
            string seedStr = Console.ReadLine() ?? "12345";
            int seed;
            if (!int.TryParse(seedStr, out seed))
            {
                seed = 12345;
            }
            string friendbergEncrypted = FriendbergEncrypt(plaintext, seed, alphabet);
            string friendbergDecrypted = FriendbergDecrypt(friendbergEncrypted, seed, alphabet);
            Console.WriteLine($"Ключ (seed): {seed}");
            Console.WriteLine($"Шифртекст:   {friendbergEncrypted}");
            Console.WriteLine($"Розшифрування: {friendbergDecrypted}");

            Console.WriteLine();
            Console.WriteLine("Натисніть Enter для завершення...");
            Console.ReadLine();
        }

        // Афінний шифр: принцип – кожну букву алфавіту відображаємо за формулою y = (a*x + b) mod m, де m – розмір алфавіту.
        // Працює як проста лінійна функція над індексами літер. Для A..Z, a=5, b=8: A(0)→(5*0+8)=8→I, B(1)→(5*1+8)=13→N тощо.
        static string AffineEncrypt(string input, int a, int b, string alphabet)
        {
            int m = alphabet.Length;
            StringBuilder result = new StringBuilder();

            foreach (char ch in input)
            {
                char c = char.ToUpper(ch);
                int index = alphabet.IndexOf(c);
                if (index < 0)
                {
                    result.Append(ch);
                }
                else
                {
                    int encIndex = (a * index + b) % m;
                    result.Append(alphabet[encIndex]);
                }
            }

            return result.ToString();
        }

        // Афінний дешифр: використовуємо обернений коефіцієнт a^(-1) за mod m та формулу x = a^(-1)*(y - b) mod m.
        // Приклад: для алфавіту A..Z, a=5, b=8, a^(-1)=21 (бо 5*21=105≡1 mod 26). Якщо y=I(8), то x = 21*(8-8)=0→A.
        static string AffineDecrypt(string input, int a, int b, string alphabet)
        {
            int m = alphabet.Length;
            int aInv = MultiplicativeInverse(a, m);
            StringBuilder result = new StringBuilder();

            foreach (char ch in input)
            {
                char c = char.ToUpper(ch);
                int index = alphabet.IndexOf(c);
                if (index < 0)
                {
                    result.Append(ch);
                }
                else
                {
                    int decIndex = aInv * (index - b);
                    decIndex %= m;
                    if (decIndex < 0) decIndex += m;
                    result.Append(alphabet[decIndex]);
                }
            }

            return result.ToString();
        }

        // Шифр Віженера: принцип – багатоалфавітна підстановка, де для кожної букви додаємо зсув, що задається відповідною буквою ключа.
        // Працює як повторювана "гама" з букв. Приклад: текст HELLO, ключ KEY: H+K→R, E+E→I, L+Y→J, L+K→V, O+E→S, результат: RIJVS.
        static string VigenereEncrypt(string input, string key, string alphabet)
        {
            int m = alphabet.Length;
            StringBuilder result = new StringBuilder();
            int keyIndex = 0;

            foreach (char ch in input)
            {
                char c = char.ToUpper(ch);
                int index = alphabet.IndexOf(c);
                if (index < 0)
                {
                    result.Append(ch);
                }
                else
                {
                    char keyChar = key[keyIndex % key.Length];
                    int keyShift = alphabet.IndexOf(keyChar);
                    int encIndex = (index + keyShift) % m;
                    result.Append(alphabet[encIndex]);
                    keyIndex++;
                }
            }

            return result.ToString();
        }

        // Дешифрування Віженера: для кожної букви віднімаємо зсув ключа за модулем m.
        // Приклад: RIJVS з ключем KEY: R-K→H, I-E→E, J-Y→L, V-K→L, S-E→O, отримуємо HELLO.
        static string VigenereDecrypt(string input, string key, string alphabet)
        {
            int m = alphabet.Length;
            StringBuilder result = new StringBuilder();
            int keyIndex = 0;

            foreach (char ch in input)
            {
                char c = char.ToUpper(ch);
                int index = alphabet.IndexOf(c);
                if (index < 0)
                {
                    result.Append(ch);
                }
                else
                {
                    char keyChar = key[keyIndex % key.Length];
                    int keyShift = alphabet.IndexOf(keyChar);
                    int decIndex = (index - keyShift) % m;
                    if (decIndex < 0) decIndex += m;
                    result.Append(alphabet[decIndex]);
                    keyIndex++;
                }
            }

            return result.ToString();
        }

        // Шифр накладання двійкової гами: принцип – XOR (додавання за модулем 2) кожного біта відкритого тексту з відповідним бітом гамми.
        // Працює симетрично: одна й та сама операція XOR шифрує й дешифрує. Приклад: текст 1011, гамма 1100 → 0111; 0111 XOR 1100 → 1011.
        static string GammaBinaryEncrypt(string bitText, string gamma)
        {
            if (string.IsNullOrEmpty(gamma))
            {
                return bitText;
            }

            StringBuilder result = new StringBuilder();
            int gLen = gamma.Length;

            for (int i = 0; i < bitText.Length; i++)
            {
                char bt = bitText[i];
                char gt = gamma[i % gLen];

                if ((bt == '0' || bt == '1') && (gt == '0' || gt == '1'))
                {
                    int b = bt == '1' ? 1 : 0;
                    int g = gt == '1' ? 1 : 0;
                    int r = b ^ g;
                    result.Append(r == 1 ? '1' : '0');
                }
                else
                {
                    result.Append(bt);
                }
            }

            return result.ToString();
        }

        // Комбінований шифр Френдберга: принцип – багатоалфавітна підстановка, де після шифрування кожної букви таблиця відповідностей змінюється
        // за псевдовипадковою перестановкою, яку задає генератор випадкових чисел (гамма). Частотний розподіл шифртексту наближається до рівномірного.
        // Простий приклад: алфавіт ABCD, початкова таблиця A→X,B→Y,C→Z,D→W. Після першої букви генератор дає число 2, ми міняємо місцями символи
        // A і C у верхньому рядку (стає CBAD), для наступної букви використовується вже інша підстановка, і так далі.
        static string FriendbergEncrypt(string input, int seed, string alphabet)
        {
            string cipherAlphabet = alphabet;
            char[] plainAlphabet = alphabet.ToCharArray();
            Random random = new Random(seed);
            StringBuilder result = new StringBuilder();

            foreach (char ch in input)
            {
                char c = char.ToUpper(ch);
                int index = Array.IndexOf(plainAlphabet, c);
                if (index < 0)
                {
                    result.Append(ch);
                }
                else
                {
                    char encChar = cipherAlphabet[index];
                    result.Append(encChar);

                    int i = random.Next(plainAlphabet.Length);
                    int j = random.Next(plainAlphabet.Length);
                    char temp = plainAlphabet[i];
                    plainAlphabet[i] = plainAlphabet[j];
                    plainAlphabet[j] = temp;
                }
            }

            return result.ToString();
        }

        // Дешифрування шифру Френдберга: використовуємо той самий генератор з тим самим seed, щоб відтворити той самий ланцюг перестановок.
        // Для кожної букви використовуємо поточну таблицю, але в зворотному напрямку: за шифр-літерою шукаємо її позицію у нижньому рядку
        // і беремо символ з верхнього рядка. Потім знову застосовуємо ту саму псевдовипадкову перестановку до верхнього рядка.
        static string FriendbergDecrypt(string input, int seed, string alphabet)
        {
            string cipherAlphabet = alphabet;
            char[] plainAlphabet = alphabet.ToCharArray();
            Random random = new Random(seed);
            StringBuilder result = new StringBuilder();

            foreach (char ch in input)
            {
                char c = char.ToUpper(ch);
                int index = cipherAlphabet.IndexOf(c);
                if (index < 0)
                {
                    result.Append(ch);
                }
                else
                {
                    char decChar = plainAlphabet[index];
                    result.Append(decChar);

                    int i = random.Next(plainAlphabet.Length);
                    int j = random.Next(plainAlphabet.Length);
                    char temp = plainAlphabet[i];
                    plainAlphabet[i] = plainAlphabet[j];
                    plainAlphabet[j] = temp;
                }
            }

            return result.ToString();
        }

        static int MultiplicativeInverse(int a, int m)
        {
            a %= m;
            if (a < 0) a += m;

            for (int x = 1; x < m; x++)
            {
                if ((a * x) % m == 1)
                {
                    return x;
                }
            }

            throw new ArgumentException("Не існує мультиплікативного оберненого елемента для заданих параметрів.");
        }
    }
}