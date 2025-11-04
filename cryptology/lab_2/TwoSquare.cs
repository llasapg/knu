using lab_2;

/*
    *** Rules ***

    1.	Перша літера шукається в лівому квадраті,
друга літера — у правому квадраті.
	2.	Якщо вони в одному рядку → обидві зсуваються вниз на один рядок (з циклом).
(аналог “один рядок” → “вниз” із Playfair, але тепер у різних таблицях).
	3.	Якщо у різних рядках → утворюється прямокутник:
	    •	перша літера → з тієї ж строки, але стовпець другої;
	    •	друга літера → з тієї ж строки, але стовпець першої.
*/


public static class TwoSquare
{
    public static string Encrypt(string plaintext, string keyLeft, string keyRight, string alphabet, Dictionary<char, char> merge, char filler)
    {
        var left = Extensions.MakeKeySquare(keyLeft, alphabet, merge);
        var right = Extensions.MakeKeySquare(keyRight, alphabet, merge);
        var text = Extensions.Normalize(plaintext, alphabet, merge);
        var digrams = Extensions.ChunkDigrams(text, filler);

        var outChars = new List<char>(digrams.Count * 2);

        foreach (var (a, b) in digrams)
        {
            var (r1, c1) = Extensions.Pos(left, a);
            var (r2, c2) = Extensions.Pos(right, b);

            if (r1 == r2) // row equals
            {
                outChars.Add(left[(r1 + 1) % 5, c1]);
                outChars.Add(right[(r2 + 1) % 5, c2]);
            }
            else // different rows --> rectangle
            {
                outChars.Add(left[r1, c2]);
                outChars.Add(right[r2, c1]);
            }
        }

        return new string([.. outChars]);
    }

    public static string Decrypt(string ciphertext, string keyLeft, string keyRight, string alphabet, Dictionary<char, char> merge)
    {
        var left = Extensions.MakeKeySquare(keyLeft, alphabet, merge);
        var right = Extensions.MakeKeySquare(keyRight, alphabet, merge);
        var text = Extensions.Normalize(ciphertext, alphabet, merge);

        if (text.Length % 2 != 0)
            throw new ArgumentException("Довжина шифртексту має бути парною.");

        var outChars = new List<char>(text.Length);

        for (int i = 0; i < text.Length; i += 2)
        {
            var a = text[i];
            var b = text[i + 1];

            var (r1, c1) = Extensions.Pos(left, a);
            var (r2, c2) = Extensions.Pos(right, b);

            if (r1 == r2)
            {
                outChars.Add(left[(r1 + 4) % 5, c1]);
                outChars.Add(right[(r2 + 4) % 5, c2]);
            }
            else
            {
                outChars.Add(left[r1, c2]);
                outChars.Add(right[r2, c1]);
            }
        }

        return new string(outChars.ToArray());
    }
}
