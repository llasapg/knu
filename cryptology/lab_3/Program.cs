using System;
using System.Numerics;
using System.Security.Cryptography;

namespace PrimalityConsoleApp;

public static class Program
{
    public static void Main(string[] args)
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;

        var numbers = new BigInteger[] { 7, 9, 17, 341, 561, 7919, 1111001110 };
        int rounds = 8;

        foreach (var n in numbers)
        {
            bool fermat = FermatPrp(n, rounds);
            Console.WriteLine($"Fermat: n={n} → {(fermat ? "ймовірно просте" : "складене")}");

            bool ss = SolovayStrassen(n, rounds);
            Console.WriteLine($"Solovay–Strassen: n={n} → {(ss ? "ймовірно просте" : "складене")}");

            bool mr = MillerRabin(n, rounds);
            Console.WriteLine($"Miller–Rabin: n={n} → {(mr ? "ймовірно просте" : "складене")}");
            Console.WriteLine();
        }

        var a = new BigInteger(7);
        var b = new BigInteger(128);
        var m = new BigInteger(19);
        var r = PowMod(a, b, m);
        Console.WriteLine($"PowMod: {a}^{b} mod {m} = {r}");
    }

    /*
        Якщо ми хочемо перевірити P на простоту, тоді ми можемо обрати випадкове A в інтервалі і подивитись чи виконується рівність.
        Якщо рівність не зберігається, значить число складене. Якщо рівність виконується для багатьох A, тоді ми кажемо, що P — можливо просте.
    */

    public static bool FermatPrp(BigInteger n, int rounds)
    {
        if (n <= 1) // 1 та менші не є простими числами
            return false;

        if (n <= 3) // 2 та 3 є простими числами
            return true;

        if (n % 2 == 0) // парні числа більші за 2 не є простими
            return false;

        // Перевіряємо рівність для кількох випадкових основ
        for (int i = 0; i < rounds; i++)
        {
            var a = RandomBase(n); // Вибираємо випадкове число a в діапазоні [2, n-2]

            if (Gcd(a, n) != 1) // Якщо a та n не взаємно прості, n є складеним
                return false;

            if (PowMod(a, n - 1, n) != 1) // Перевіряємо рівність Ферма
                return false;
        }

        return true;
    }

    /*
        Якщо n — просте число, тоді (a/n) ≡ a^((n-1)/2) (mod n) для будь-якого a, взаємно простого з n.
        Якщо n — складене число, тоді ймовірність того, що ця рівність виконується для випадкового a, не більша за 1/2.
    */

    public static bool SolovayStrassen(BigInteger n, int rounds)
    {
        if (n <= 1) // 1 та менші не є простими числами
            return false;

        if (n == 2 || n == 3) // 2 та 3 є простими числами
            return true;

        if (n % 2 == 0) // парні числа більші за 2 не є простими
            return false;

        // Перевіряємо умову Соловає-Штрассена для кількох випадкових основ
        for (int i = 0; i < rounds; i++)
        {
            var a = RandomBase(n); // Вибираємо випадкове число a в діапазоні [2, n-2]
            var g = Gcd(a, n); // Обчислюємо НСД(a, n)

            if (g > 1) // Якщо НСД більший за 1, n є складеним
                return false;

            var x = Jacobi(a, n); // Обчислюємо символ Якобі (a/n)

            if (x == 0) // Якщо символ Якобі дорівнює 0, n є складеним
                return false;

            var y = PowMod(a, (n - 1) / 2, n); // Обчислюємо a^((n-1)/2) mod n

            var xp = x < 0 ? n - 1 : 1; // Перетворюємо символ Якобі в відповідне значення мод n

            if ((y - xp) % n != 0) // Перевіряємо умову Соловає-Штрассена
                return false;
        }

        return true;
    }

    /*
        Якщо n — просте число, тоді для будь-якого a в інтервалі [2, n-2] виконується:
        a^d ≡ 1 (mod n) або a^{2^r * d} ≡ -1 (mod n) для деякого 0 ≤ r < s,
        де n-1 = 2^s * d з непарним d.

        Якщо n — складене число, тоді ймовірність того, що ця умова виконується для випадкового a, не більша за 1/4.
    */

    public static bool MillerRabin(BigInteger n, int rounds)
    {
        if (n <= 1)
            return false;

        if (n <= 3)
            return true;

        if (n % 2 == 0)
            return false;

        (int s, BigInteger d) = Decompose(n - 1); // Розкладаємо n-1 на 2^s * d

        // Перевіряємо умову Міллера-Рабіна для кількох випадкових основ
        for (int i = 0; i < rounds; i++)
        {
            // Вибираємо випадкове число a в діапазоні [2, n-2]
            var a = RandomBase(n);

            // Перевіряємо, чи є a свідком складеності n
            if (IsWitness(a, n, s, d))
                return false;
        }

        return true;
    }

    private static (int s, BigInteger d) Decompose(BigInteger nMinusOne)
    {
        int s = 0;

        BigInteger d = nMinusOne;

        while ((d & 1) == 0)
        {
            d >>= 1;
            s++;
        }

        return (s, d);
    }

    private static bool IsWitness(BigInteger a, BigInteger n, int s, BigInteger d)
    {
        BigInteger x = PowMod(a, d, n);

        if (x == 1 || x == n - 1)
            return false;

        for (int r = 1; r < s; r++)
        {
            x = (x * x) % n;
            if (x == n - 1)
                return false;
        }

        return true;
    }

    /*
        Обчислює (b^e) mod m за допомогою швидкого піднесення до степеня за модулем.
    */

    public static BigInteger PowMod(BigInteger b, BigInteger e, BigInteger m)
    {
        if (m == 1) // будь-яке число за модулем 1 дорівнює 0
            return 0;

        b %= m; // забезпечуємо, що b знаходиться в межах модуля

        if (b < 0) // обробка від'ємних основ
            b += m;

        BigInteger res = 1; // початкове значення результату

        while (e > 0) // поки степінь не дорівнює нулю
        {
            if (!e.IsEven) // якщо поточний біт степеня є 1
                res = res * b % m; // множимо результат на поточну основу

            b = b * b % m; // піднесення основи до квадрату
            e >>= 1; // зсув степеня вправо (ділення на 2)
        }

        return res;
    }

    private static BigInteger Gcd(BigInteger a, BigInteger b)
    {
        while (b != 0)
        {
            var t = b;
            b = a % b;
            a = t;
        }

        return BigInteger.Abs(a);
    }

    private static BigInteger RandomBase(BigInteger n)
    {
        if (n <= 4)
            return 2;

        BigInteger a;

        do
        {
            a = RandomBetween(2, n - 2);
        } while (a < 2 || a > n - 2);

        return a;
    }

    private static BigInteger RandomBetween(BigInteger min, BigInteger max)
    {
        if (min > max)
            throw new ArgumentException("min > max");

        var diff = max - min + 1;

        int bytes = (int)Math.Ceiling(BigInteger.Log(diff, 2) / 8.0);

        if (bytes < 1)
            bytes = 1;

        byte[] buffer = new byte[bytes + 1];
        BigInteger r;

        do
        {
            RandomNumberGenerator.Fill(buffer);
            buffer[^1] = 0;
            r = new BigInteger(buffer);
        } while (r >= diff);

        return min + r;
    }

    private static int Jacobi(BigInteger a, BigInteger n)
    {
        if (n <= 0 || n.IsEven)
            throw new ArgumentException("n must be positive odd");

        a %= n;
        int result = 1;
        while (a != 0)
        {
            while (a.IsEven)
            {
                a >>= 1;
                var nMod8 = (int)(n % 8);
                if (nMod8 == 3 || nMod8 == 5) result = -result;
            }

            (a, n) = (n, a);
            if ((a % 4 == 3) && (n % 4 == 3)) result = -result;
            a %= n;
        }
        return n == 1 ? result : 0;
    }
}