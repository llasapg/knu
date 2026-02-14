using System;
using System.Text;

class Program
{
    static void Main(string[] args)
    {
        Console.WriteLine("Введіть текст для SHA-1:");
        string input = Console.ReadLine();

        string hash = ComputeSHA1(input);
        Console.WriteLine("\nSHA-1 хеш:");
        Console.WriteLine(hash);

        Console.ReadLine();
    }

    // ============================================================
    // ГОЛОВНА ФУНКЦІЯ ХЕШУВАННЯ SHA-1
    // Виконує повний процес: кодування → доповнення → обробка блоків → формування хешу
    // ============================================================
    static string ComputeSHA1(string input)
    {
        byte[] message = Encoding.UTF8.GetBytes(input);
        byte[] padded = PadMessage(message);
        uint[] H = InitializeHashValues();

        ProcessBlocks(padded, H);

        return HashToString(H);
    }

    // ============================================================
    // ДОПОВНЕННЯ ПОВІДОМЛЕННЯ ЗА СТАНДАРТОМ SHA-1 (ВИПРАВЛЕНО)
    // Додає 0x80, потім нулі до довжини % 64 == 56, потім 64 біти довжини
    // ============================================================
    static byte[] PadMessage(byte[] message)
    {
        ulong bitLength = (ulong)message.Length * 8;

        int padding = 56 - (message.Length + 1) % 64;

        if (padding < 0)
            padding += 64;

        byte[] padded = new byte[message.Length + 1 + padding + 8];

        Array.Copy(message, padded, message.Length);

        padded[message.Length] = 0x80;

        byte[] lengthBytes = BitConverter.GetBytes(bitLength);
        if (BitConverter.IsLittleEndian)
            Array.Reverse(lengthBytes);

        Array.Copy(lengthBytes, 0, padded, padded.Length - 8, 8);

        return padded;
    }

    // ============================================================
    // ІНІЦІАЛІЗАЦІЯ ПОЧАТКОВИХ ЗНАЧЕНЬ ХЕШ-РЕГІСТРІВ SHA-1
    // Повертає масив h0..h4 — стандартні константи SHA-1
    // ============================================================
    static uint[] InitializeHashValues()
    {
        return
        [
            0x67452301,
            0xEFCDAB89,
            0x98BADCFE,
            0x10325476,
            0xC3D2E1F0
        ];
    }

    // ============================================================
    // ОБРОБКА ВСІХ 512-БІТНИХ БЛОКІВ ПОВІДОМЛЕННЯ
    // Для кожного блоку формує W[0..79] і запускає SHA-1 раунди
    // ============================================================
    static void ProcessBlocks(byte[] padded, uint[] H)
    {
        int blockCount = padded.Length / 64;

        for (int i = 0; i < blockCount; i++)
        {
            uint[] W = PrepareMessageSchedule(padded, i);
            ProcessBlock(W, H);
        }
    }

    // ============================================================
    // ФОРМУВАННЯ МАСИВУ W[0..79]
    // Перші 16 слів — з блоку. Інші — генеруються через XOR і зсув.
    // ============================================================
    static uint[] PrepareMessageSchedule(byte[] padded, int blockIndex)
    {
        uint[] W = new uint[80];
        int start = blockIndex * 64;

        for (int t = 0; t < 16; t++)
        {
            W[t] = (uint)(
                (padded[start + t * 4] << 24) |
                (padded[start + t * 4 + 1] << 16) |
                (padded[start + t * 4 + 2] << 8) |
                padded[start + t * 4 + 3]
            );
        }

        for (int t = 16; t < 80; t++)
        {
            W[t] = LeftRotate(W[t - 3] ^ W[t - 8] ^ W[t - 14] ^ W[t - 16], 1);
        }

        return W;
    }

    // ============================================================
    // ОБРОБКА ОДНОГО 512-БІТНОГО БЛОКУ SHA-1
    // Виконує 80 раундів з різними логічними функціями та константами
    // ============================================================
    static void ProcessBlock(uint[] W, uint[] H)
    {
        uint A = H[0];
        uint B = H[1];
        uint C = H[2];
        uint D = H[3];
        uint E = H[4];

        for (int t = 0; t < 80; t++)
        {
            uint f, K;

            if (t < 20)
            {
                f = (B & C) | ((~B) & D);
                K = 0x5A827999;
            }
            else if (t < 40)
            {
                f = B ^ C ^ D;
                K = 0x6ED9EBA1;
            }
            else if (t < 60)
            {
                f = (B & C) | (B & D) | (C & D);
                K = 0x8F1BBCDC;
            }
            else
            {
                f = B ^ C ^ D;
                K = 0xCA62C1D6;
            }

            uint temp = LeftRotate(A, 5) + f + E + W[t] + K;

            E = D;
            D = C;
            C = LeftRotate(B, 30);
            B = A;
            A = temp;
        }

        H[0] += A;
        H[1] += B;
        H[2] += C;
        H[3] += D;
        H[4] += E;
    }

    // ============================================================
    // ФУНКЦІЯ ЦИКЛІЧНОГО ЗСУВУ ВЛІВО
    // Повертає число зі зсунутих бітом, типовий оператор для SHA
    // ============================================================
    static uint LeftRotate(uint value, int bits)
    {
        return (value << bits) | (value >> (32 - bits));
    }

    // ============================================================
    // ПЕРЕТВОРЕННЯ ХЕШ-РЕЗУЛЬТАТУ У РЯДОК HEX-ФОРМАТУ
    // Формує фінальний 160-бітний SHA-1 дайджест
    // ============================================================
    static string HashToString(uint[] H)
    {
        StringBuilder sb = new StringBuilder();

        foreach (uint h in H)
        {
            sb.Append(h.ToString("X8"));
        }

        return sb.ToString();
    }
}