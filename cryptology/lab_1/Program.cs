using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace TranspositionCiphers
{
    public static class Utils
    {
        public static string Normalize(string s, char pad = 'Х')
        {
            if (string.IsNullOrEmpty(s)) return string.Empty;
            var sb = new StringBuilder();
            foreach (var ch in s.ToUpperInvariant())
            {
                if (char.IsLetterOrDigit(ch) || ch == ' ')
                {
                    if (ch == 'Ё') sb.Append('Е');
                    else sb.Append(ch);
                }
            }
            return sb.ToString();
        }

        public static char[,] FillRowWise(string text, int rows, int cols, char pad = 'Х')
        {
            var grid = new char[rows, cols];
            int k = 0;
            for (int r = 0; r < rows; r++)
                for (int c = 0; c < cols; c++)
                    grid[r, c] = k < text.Length ? text[k++] : pad;
            return grid;
        }

        public static string ReadColWise(char[,] grid)
        {
            int rows = grid.GetLength(0);
            int cols = grid.GetLength(1);
            var sb = new StringBuilder(rows * cols);
            for (int c = 0; c < cols; c++)
                for (int r = 0; r < rows; r++)
                    sb.Append(grid[r, c]);
            return sb.ToString();
        }

        public static string ReadRowWise(char[,] grid)
        {
            int rows = grid.GetLength(0);
            int cols = grid.GetLength(1);
            var sb = new StringBuilder(rows * cols);
            for (int r = 0; r < rows; r++)
                for (int c = 0; c < cols; c++)
                    sb.Append(grid[r, c]);
            return sb.ToString();
        }

        public static int[] KeyToPermutation(string key)
        {
            // Returns a permutation where perm[newIndex] = oldIndex after sorting by key ascending (stable)
            var arr = key.Select((ch, idx) => (ch, idx)).ToList();
            var ordered = arr
                .Select(x => (x.ch, x.idx, rank: x.ch, tie: x.idx))
                .OrderBy(x => x.rank)
                .ThenBy(x => x.tie)
                .ToList();
            int[] perm = new int[ordered.Count];
            for (int newIdx = 0; newIdx < ordered.Count; newIdx++)
                perm[newIdx] = ordered[newIdx].idx;
            return perm;
        }

        public static int[] InvertPermutation(int[] perm)
        {
            // Given perm[new] = old, return inv[old] = new
            int n = perm.Length;
            var inv = new int[n];
            for (int i = 0; i < n; i++) inv[perm[i]] = i;
            return inv;
        }

        public static char[,] PermuteRows(char[,] grid, int[] permNewToOld)
        {
            int rows = grid.GetLength(0);
            int cols = grid.GetLength(1);
            var res = new char[rows, cols];
            for (int newR = 0; newR < rows; newR++)
            {
                int oldR = permNewToOld[newR];
                for (int c = 0; c < cols; c++)
                    res[newR, c] = grid[oldR, c];
            }
            return res;
        }

        public static char[,] PermuteCols(char[,] grid, int[] permNewToOld)
        {
            int rows = grid.GetLength(0);
            int cols = grid.GetLength(1);
            var res = new char[rows, cols];
            for (int newC = 0; newC < cols; newC++)
            {
                int oldC = permNewToOld[newC];
                for (int r = 0; r < rows; r++)
                    res[r, newC] = grid[r, oldC];
            }
            return res;
        }

        public static void PrintGrid(char[,] grid, string title = null)
        {
            if (!string.IsNullOrEmpty(title)) Console.WriteLine(title);
            int rows = grid.GetLength(0);
            int cols = grid.GetLength(1);
            for (int r = 0; r < rows; r++)
            {
                for (int c = 0; c < cols; c++)
                {
                    Console.Write(grid[r, c]);
                    if (c + 1 < cols) Console.Write(' ');
                }
                Console.WriteLine();
            }
            Console.WriteLine();
        }
    }
    // ===== 1) Звичайна (блокова) перестановка =====
    public static class SimplePermutationCipher
    {
        // perm[j] = old index in block that goes to new position j
        public static string Encrypt(string plaintext, int[] perm, char pad = 'Х')
        {
            int blockSize = perm.Length;

            plaintext = Utils.Normalize(plaintext, pad).Replace(" ", string.Empty);
            var sb = new StringBuilder();

            for (int i = 0; i < plaintext.Length; i += blockSize)
            {
                var block = new char[blockSize];

                for (int j = 0; j < blockSize; j++)
                {
                    int src = i + perm[j];
                    block[j] = src < plaintext.Length ? plaintext[src] : pad;
                }

                sb.Append(block);
            }

            return sb.ToString();
        }

        public static string Decrypt(string ciphertext, int[] perm, char pad = 'Х')
        {
            int n = perm.Length;
            var sb = new StringBuilder(ciphertext.Length);

            for (int i = 0; i < ciphertext.Length; i += n)
            {
                var block = new char[n];

                for (int j = 0; j < n; j++)
                {
                    int src = i + j;
                    int dst = perm[j];
                    block[dst] = src < ciphertext.Length ? ciphertext[src] : pad;
                }

                sb.Append(block);
            }

            return sb.ToString().TrimEnd(pad);
        }
    }

    // ===== 2) Звичайна рядково-стовпчикова таблична перестановка (без ключів) =====
    public static class PlainRowColumnTransposition
    {
        public static string Encrypt(string plaintext, int rows, int cols, char pad = 'Х')
        {
            plaintext = Utils.Normalize(plaintext, pad).Replace(" ", string.Empty);
            var grid = Utils.FillRowWise(plaintext, rows, cols, pad);
            return Utils.ReadColWise(grid);
        }
        public static string Decrypt(string ciphertext, int rows, int cols)
        {
            var grid = new char[rows, cols];
            int k = 0;
            for (int c = 0; c < cols; c++)
                for (int r = 0; r < rows; r++)
                    grid[r, c] = k < ciphertext.Length ? ciphertext[k++] : 'Х';
            return Utils.ReadRowWise(grid);
        }
    }

    // ===== 3) Рядково-стовпчикова з ключем стовпців =====
    public static class ColumnKeyTransposition
    {
        public static string Encrypt(string plaintext, string colKey, char pad = 'Х')
        {
            plaintext = Utils.Normalize(plaintext, pad).Replace(" ", string.Empty);
            int cols = colKey.Length;
            int rows = (int)Math.Ceiling(plaintext.Length / (double)cols);
            var grid = Utils.FillRowWise(plaintext, rows, cols, pad);
            var colPerm = Utils.KeyToPermutation(colKey);
            var permuted = Utils.PermuteCols(grid, colPerm);
            return Utils.ReadColWise(permuted);
        }
        public static string Decrypt(string ciphertext, string colKey)
        {
            int cols = colKey.Length;
            int rows = (int)Math.Ceiling(ciphertext.Length / (double)cols);
            // наповнюємо по стовпцях у вже переставлену-стовпцями сітку
            var permuted = new char[rows, cols];
            int k = 0;
            for (int c = 0; c < cols; c++)
                for (int r = 0; r < rows; r++)
                    permuted[r, c] = k < ciphertext.Length ? ciphertext[k++] : 'Х';
            // прибираємо перестановку стовпців
            var invCol = Utils.InvertPermutation(Utils.KeyToPermutation(colKey));
            var unperm = Utils.PermuteCols(permuted, invCol);
            return Utils.ReadRowWise(unperm);
        }
    }

    // ===== 4) Рядково-стовпчикова з ключем рядків =====
    public static class RowKeyTransposition
    {
        public static string Encrypt(string plaintext, string rowKey, char pad = 'Х')
        {
            plaintext = Utils.Normalize(plaintext, pad).Replace(" ", string.Empty);
            int rows = rowKey.Length;
            int cols = (int)Math.Ceiling(plaintext.Length / (double)rows);
            var grid = Utils.FillRowWise(plaintext, rows, cols, pad);
            var rowPerm = Utils.KeyToPermutation(rowKey);
            var permuted = Utils.PermuteRows(grid, rowPerm);
            return Utils.ReadColWise(permuted);
        }
        public static string Decrypt(string ciphertext, string rowKey)
        {
            int rows = rowKey.Length;
            int cols = (int)Math.Ceiling(ciphertext.Length / (double)rows);
            var permuted = new char[rows, cols];
            int k = 0;
            for (int c = 0; c < cols; c++)
                for (int r = 0; r < rows; r++)
                    permuted[r, c] = k < ciphertext.Length ? ciphertext[k++] : 'Х';
            var invRow = Utils.InvertPermutation(Utils.KeyToPermutation(rowKey));
            var unperm = Utils.PermuteRows(permuted, invRow);
            return Utils.ReadRowWise(unperm);
        }
    }

    public static class DoubleKeyRowColumn
    {
        // Encrypt: fill row-wise; permute rows by rowKey, then columns by colKey; read column-wise
        public static string Encrypt(string plaintext, string rowKey, string colKey, char pad = 'Х')
        {
            plaintext = Utils.Normalize(plaintext, pad).Replace(" ", string.Empty);
            int rows = rowKey.Length;
            int cols = colKey.Length;
            var grid = Utils.FillRowWise(plaintext, rows, cols, pad);

            var rowPerm = Utils.KeyToPermutation(rowKey);
            var colPerm = Utils.KeyToPermutation(colKey);
            var permutedRows = Utils.PermuteRows(grid, rowPerm);
            var permutedBoth = Utils.PermuteCols(permutedRows, colPerm);

            return Utils.ReadColWise(permutedBoth);
        }

        // Decrypt is the inverse: reshape, fill column-wise into permuted grid; undo col perm, then row perm; read row-wise
        public static string Decrypt(string ciphertext, string rowKey, string colKey)
        {
            int rows = rowKey.Length;
            int cols = colKey.Length;
            var grid = new char[rows, cols];

            int k = 0;
            for (int c = 0; c < cols; c++)
                for (int r = 0; r < rows; r++)
                    grid[r, c] = ciphertext[k++];

            var colPerm = Utils.KeyToPermutation(colKey);
            var invCol = Utils.InvertPermutation(colPerm);
            var rowPerm = Utils.KeyToPermutation(rowKey);
            var invRow = Utils.InvertPermutation(rowPerm);

            var unpermCols = Utils.PermuteCols(grid, invCol);
            var unpermRows = Utils.PermuteRows(unpermCols, invRow);

            return Utils.ReadRowWise(unpermRows);
        }
    }

    public static class CardanoGrille
    {
        public struct Pos { public int R; public int C; public Pos(int r, int c) { R = r; C = c; } }

        public static Pos Rotate(Pos p, int n) => new Pos(p.C, n - 1 - p.R); // 90° clockwise

        public static List<Pos> AllHoles(List<Pos> baseHoles, int n)
        {
            var res = new List<Pos>();
            var current = baseHoles.ToList();
            for (int rot = 0; rot < 4; rot++)
            {
                res.AddRange(current);
                // rotate all
                current = current.Select(p => Rotate(p, n)).ToList();
            }
            return res;
        }

        public static bool IsValidGrille(List<Pos> baseHoles, int n)
        {
            var holes = AllHoles(baseHoles, n);
            if (holes.Count != n * n) return false;
            var set = new HashSet<(int, int)>();
            foreach (var h in holes)
            {
                if (!set.Add((h.R, h.C))) return false; // overlap
            }
            return true;
        }

        public static string Encrypt(string plaintext, int n, List<Pos> baseHoles, char pad = 'Х')
        {
            plaintext = Utils.Normalize(plaintext, pad).Replace(" ", string.Empty);
            var grid = new char[n, n];
            for (int r = 0; r < n; r++) for (int c = 0; c < n; c++) grid[r, c] = pad;

            var current = baseHoles.ToList();
            int k = 0;
            for (int rot = 0; rot < 4; rot++)
            {
                foreach (var h in current)
                {
                    grid[h.R, h.C] = k < plaintext.Length ? plaintext[k++] : pad;
                }
                current = current.Select(p => Rotate(p, n)).ToList();
            }
            return Utils.ReadRowWise(grid);
        }

        public static string Decrypt(string ciphertext, int n, List<Pos> baseHoles)
        {
            var grid = Utils.FillRowWise(ciphertext, n, n);
            var sb = new StringBuilder(ciphertext.Length);
            var current = baseHoles.ToList();
            for (int rot = 0; rot < 4; rot++)
            {
                foreach (var h in current)
                    sb.Append(grid[h.R, h.C]);
                current = current.Select(p => Rotate(p, n)).ToList();
            }
            return sb.ToString();
        }
    }

    class Program
    {
        static void Main()
        {
            Console.OutputEncoding = Encoding.UTF8;

            // ===== 1) Звичайна (блокова) перестановка =====
            string pt1 = "КРИПТОГРАФІЯ";
            int[] perm = { 2, 0, 3, 1 }; // приклад для блоку 4: нові позиції [0..3] беруть 2,0,3,1 із старого блоку
            string ct1 = SimplePermutationCipher.Encrypt(pt1, perm);
            string dec1 = SimplePermutationCipher.Decrypt(ct1, perm);
            Console.WriteLine("[1] Звичайна перестановка");
            Console.WriteLine($"PT: {pt1} CT: {ct1} DEC: {dec1}");

            // ===== 2) Звичайна рядково-стовпчикова (без ключів) =====
            string pt2 = "ТАБЛИЧНАПЕРЕСТАНОВКА";
            string ct2 = PlainRowColumnTransposition.Encrypt(pt2, 3, 8); // 3x8
            string dec2 = PlainRowColumnTransposition.Decrypt(ct2, 3, 8);
            Console.WriteLine("[2] Рядково-стовпчикова без ключів");
            Console.WriteLine($"PT: {pt2} CT: {ct2} DEC: {dec2}");

            // ===== 3) З ключем стовпців =====
            string pt3 = "ПРИКЛАДКОЛОНАРНОЇПЕРЕСТАНОВКИ";
            string keyCols = "ШКОЛА";
            string ct3 = ColumnKeyTransposition.Encrypt(pt3, keyCols);
            string dec3 = ColumnKeyTransposition.Decrypt(ct3, keyCols);
            Console.WriteLine("[3] Ключ стовпців");
            Console.WriteLine($"PT: {pt3} KeyCols: {keyCols} CT: {ct3} DEC: {dec3}");

            // ===== 4) З ключем рядків =====
            string pt4 = "ПРИКЛАДПЕРЕСТАНОВКИЗКЛЮЧЕМРЯДКІВ";
            string keyRows = "БУРЯ";
            string ct4 = RowKeyTransposition.Encrypt(pt4, keyRows);
            string dec4 = RowKeyTransposition.Decrypt(ct4, keyRows);
            Console.WriteLine("[4] Ключ рядків");
            Console.WriteLine($"PT: {pt4} KeyRows: {keyRows} CT: {ct4} DEC: {dec4}");

            // ===== 5) Подвійна (рядки + стовпці) =====
            string pt5 = "КРИПТОГРАФІЯ ЦЕ ЦІКАВО";
            string rowKey = "БУРЯ";   // 4 рядки
            string colKey = "ШКОЛА";  // 5 стовпців
            var ct5 = DoubleKeyRowColumn.Encrypt(pt5, rowKey, colKey);
            var dec5 = DoubleKeyRowColumn.Decrypt(ct5, rowKey, colKey);
            Console.WriteLine("[5] Подвійна ключова перестановка");
            Console.WriteLine($"PT: {pt5} RowKey: {rowKey}, ColKey: {colKey} CT: {ct5} DEC: {dec5}");

            // ===== 6) Трафарет Кардано =====
            var baseHoles = new List<CardanoGrille.Pos>
            {
                // валідний базовий набір для n=4 (1 з кожної орбіти)
                new CardanoGrille.Pos(0,0),
                new CardanoGrille.Pos(0,1),
                new CardanoGrille.Pos(0,2),
                new CardanoGrille.Pos(1,1)
            };

            int n = 4;
            if (!CardanoGrille.IsValidGrille(baseHoles, n))
            {
                Console.WriteLine("Помилка: трафарет не валідний");
            }
            string pt6 = "ТАЄМНЕПОВІДОМЛЕННЯ";
            var ct6 = CardanoGrille.Encrypt(pt6, n, baseHoles);
            var dec6 = CardanoGrille.Decrypt(ct6, n, baseHoles);
            Console.WriteLine("[6] Трафарет Кардано");
            Console.WriteLine($"PT: {pt6}CT: {ct6}DEC: {dec6}");



        }
    }
}
