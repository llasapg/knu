using lab_2;

var alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ";
var merge = new Dictionary<char, char> { ['J'] = 'I' };
var filler = 'X';

var pt = "BLA BLA CAR 2357-!!!!!!             %_asd";

var keyPf = "PLAYFAIR EXAMPLE";
var ctPf = Playfair.Encrypt(pt, keyPf, alphabet, merge, filler);
var dtPf = Playfair.Decrypt(ctPf, keyPf, alphabet, merge, filler);

Console.WriteLine("Біграмний шифр Плейфера");
Console.WriteLine($"PT: {pt}");
Console.WriteLine($"CT: {ctPf}");
Console.WriteLine($"DT: {dtPf}");
Console.WriteLine();

var keyLeft = "EXAMPLE LEFT";
var keyRight = "SAMPLE RIGHT";
var ctTs = TwoSquare.Encrypt(pt, keyLeft, keyRight, alphabet, merge, filler);
var dtTs = TwoSquare.Decrypt(ctTs, keyLeft, keyRight, alphabet, merge);

Console.WriteLine("Біграмний двотабличний шифр (Two-Square)");
Console.WriteLine($"PT: {pt}");
Console.WriteLine($"CT: {ctTs}");
Console.WriteLine($"DT: {dtTs}");