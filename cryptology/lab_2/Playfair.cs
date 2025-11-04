using lab_2;

public static class Playfair
{
    /*
        1 Побудова 5×5 квадрата з ключа
        2 Підготовка тексту (очищення, біграми)
        3 Заміна пар за трьома правилами
        4 Отримання шифртексту
    */

    /*
        *** Rules ***

        1.	Якщо в одному рядку — заміни кожну літеру на наступну праворуч (із циклом).
    приклад: AR → RE
        2.	Якщо в одному стовпці — заміни кожну літеру на наступну вниз (із циклом).
    приклад: DM → HE
        3.	Якщо в різних рядках і стовпцях — утвори прямокутник, і заміни кожну літеру на літеру з тієї ж строки, але зі стовпця другої літери.
    */

    public static string Encrypt(string plaintext, string key, string alphabet, Dictionary<char, char> merge, char filler)
    {
        var sq = Extensions.MakeKeySquare(key, alphabet, merge);
        var text = Extensions.Normalize(plaintext, alphabet, merge);
        var digrams = Extensions.ChunkDigrams(text, filler);
        var outChars = new List<char>(digrams.Count * 2);

        foreach (var (a, b) in digrams)
        {
            var (r1, c1) = Extensions.Pos(sq, a);
            var (r2, c2) = Extensions.Pos(sq, b);

            if (r1 == r2) // row equals
            {
                outChars.Add(sq[r1, (c1 + 1) % 5]);
                outChars.Add(sq[r2, (c2 + 1) % 5]);
            }
            else if (c1 == c2) // column equals
            {
                outChars.Add(sq[(r1 + 1) % 5, c1]);
                outChars.Add(sq[(r2 + 1) % 5, c2]);
            }
            else
            {
                outChars.Add(sq[r1, c2]);
                outChars.Add(sq[r2, c1]);
            }
        }

        return new string(outChars.ToArray());
    }

    public static string Decrypt(string ciphertext, string key, string alphabet, Dictionary<char, char> merge, char filler)
    {
        var sq = Extensions.MakeKeySquare(key, alphabet, merge);
        var text = Extensions.Normalize(ciphertext, alphabet, merge);

        if (text.Length % 2 != 0)
            throw new ArgumentException("Довжина шифртексту має бути парною.");

        var outChars = new List<char>(text.Length);

        for (int i = 0; i < text.Length; i += 2)
        {
            var a = text[i];
            var b = text[i + 1];

            var (r1, c1) = Extensions.Pos(sq, a);
            var (r2, c2) = Extensions.Pos(sq, b);

            if (r1 == r2)
            {
                outChars.Add(sq[r1, (c1 + 4) % 5]);
                outChars.Add(sq[r2, (c2 + 4) % 5]);
            }
            else if (c1 == c2)
            {
                outChars.Add(sq[(r1 + 4) % 5, c1]);
                outChars.Add(sq[(r2 + 4) % 5, c2]);
            }
            else
            {
                outChars.Add(sq[r1, c2]);
                outChars.Add(sq[r2, c1]);
            }
        }

        return new string([.. outChars]);
    }
}
