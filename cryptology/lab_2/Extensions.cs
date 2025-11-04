using System.Text.RegularExpressions;

namespace lab_2;

public static partial class Extensions
{
    public static string Normalize(string text, string alphabet, Dictionary<char, char> merge)
    {
        var t = MyRegex().Replace(text, "").ToUpperInvariant();
        var mapped = new char[t.Length];
        for (int i = 0; i < t.Length; i++)
        {
            var ch = t[i];
            if (merge != null && merge.TryGetValue(ch, out var rep)) ch = rep;
            mapped[i] = ch;
        }
        var set = new HashSet<char>(alphabet);
        var list = new List<char>(mapped.Length);
        foreach (var ch in mapped)
            if (set.Contains(ch)) list.Add(ch);
        return new string(list.ToArray());
    }

    public static (int r, int c) Pos(char[,] sq, char ch)
    {
        for (int r = 0; r < 5; r++)
            for (int c = 0; c < 5; c++)
                if (sq[r, c] == ch) return (r, c);
        throw new ArgumentException($"Символ {ch} не знайдено у квадраті.");
    }

    public static List<(char a, char b)> ChunkDigrams(string text, char filler)
    {
        var res = new List<(char a, char b)>();
        int i = 0;
        while (i < text.Length)
        {
            var a = text[i];
            if (i + 1 < text.Length)
            {
                var b = text[i + 1];
                if (a == b)
                {
                    res.Add((a, filler));
                    i += 1;
                }
                else
                {
                    res.Add((a, b));
                    i += 2;
                }
            }
            else
            {
                res.Add((a, filler));
                i += 1;
            }
        }
        return res;
    }

    public static char[,] MakeKeySquare(string key, string alphabet, Dictionary<char, char> merge)
    {
        var k = Normalize(key, alphabet, merge);
        var used = new HashSet<char>();
        var seq = new List<char>(25);
        foreach (var ch in (k + alphabet))
            if (!used.Contains(ch) && alphabet.IndexOf(ch) >= 0)
            {
                used.Add(ch);
                seq.Add(ch);
            }
        if (seq.Count != 25) throw new ArgumentException("Алфавіт має містити 25 унікальних символів.");
        var sq = new char[5, 5];
        int idx = 0;
        for (int r = 0; r < 5; r++)
            for (int c = 0; c < 5; c++)
                sq[r, c] = seq[idx++];
        return sq;
    }

    [GeneratedRegex("[^A-Za-zА-Яа-яЁёІіЇїЄєҐґ]")]
    private static partial Regex MyRegex();
}