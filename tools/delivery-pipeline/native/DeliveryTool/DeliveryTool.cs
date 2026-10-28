// DeliveryTool — AutoCAD Core Console commands for detached Advance Steel shop-drawing delivery.
// Every command reads its parameters from environment variables or a UTF-8 JSON job file
// (Core Console .scr files must stay ASCII; Chinese paths go through env/JSON), writes a JSON
// report, never overwrites an existing output, and reports success=false instead of throwing.
//
// Common env:
//   DT_LAYOUT   paper layout name (default "A3 Advance Steel")
//
// Commands
//   DTINSPECT    read-only inventory of every layout + frame blocks        DT_REPORT
//   DTPROBE      read-only texts inside A$C frame blocks (title/scale)      DT_REPORT
//   DTAPPLY      erase old frame handles, insert donor frame per page       DT_JOB (ApplyJob json)
//   DTCOVER      replace project name in cover MText                        DT_OUTPUT DT_REPORT DT_FROM DT_TO DT_EXPECT_COUNT
//   DTINDEX      draw a drawing-list table (run after DTAPPLY)              DT_INDEX_JOB (IndexJob json)
//   DTPLOTALL    window plot each page to its own PDF                       DT_PLOTS (json array)
//   DTCHECKFRAME read-only: texts inside inserted DT_FRAME_* blocks         DT_REPORT
//   DTATTRREAD   read-only: header block attributes and placement           DT_REPORT DT_BLOCK
//   DTSETATTR    set exactly one attribute (old value must match)           DT_OUTPUT DT_REPORT DT_BLOCK DT_TAG DT_FROM DT_TO
//   DTPROJFILL   fill blank PROJECT-style attribute, unify height/position  DT_OUTPUT DT_REPORT DT_BLOCK DT_TAG DT_NAME DT_HEIGHT DT_ALIGNY
//
// Do NOT Explode HYPERSTEELPAGEHEADER or walk its definition geometry: Core Console crashes.
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;
using Autodesk.AutoCAD.PlottingServices;
using Autodesk.AutoCAD.Runtime;
using System.Globalization;
using System.Text.Json;

[assembly: CommandClass(typeof(DeliveryTool.Commands))]
namespace DeliveryTool;

public record PageJob(string Number, string Title, double X, double ShiftY, string? Scale = null);
public record ApplyJob(
    string Donor, string Output, string Report, string[] Erase, PageJob[] Pages,
    string DonorTitleText,                // exact title text in the donor frame to replace
    string DonorScaleText = "比例：NTS",   // exact scale text in the donor frame
    string ScalePrefix = "比例：",
    string ScaleFallback = "詳各視圖",
    double[]? NumberPos = null,           // drawing-number text inside the frame (x,y,height,width)
    double[]? MarkPos = null,             // big on-sheet page marker (x,y,height); null = none
    string NumberLayer = "DT_DRAWING_NUMBER",
    double BottomBandY = 26.0,            // frame entities fully below this move with ShiftY
    int MinDonorEntities = 50);
public record IndexRow(string Number, string Category, string Title, int BookPage);
public record IndexJob(
    string Output, string Report, string RowsFile, string Title, string Subtitle = "",
    int MaxRows = 20, string FontFile = "kaiu.ttf", string[]? Headers = null);

public class Commands
{
    static string? lastApplied;
    static string Env(string k) => Environment.GetEnvironmentVariable(k) ?? throw new InvalidOperationException("Missing env " + k);
    static string EnvOr(string k, string d) => Environment.GetEnvironmentVariable(k) is { Length: > 0 } v ? v : d;
    static double EnvD(string k) => double.Parse(Env(k), CultureInfo.InvariantCulture);
    static string LayoutName => EnvOr("DT_LAYOUT", "A3 Advance Steel");
    static Database Db => Application.DocumentManager.MdiActiveDocument.Database;
    static readonly JsonSerializerOptions Utf8 = new() { Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping };
    static void Write(string path, object o) => File.WriteAllText(path, JsonSerializer.Serialize(o, Utf8));
    static void Fail(string report, System.Exception ex) => Write(report, new { success = false, error = ex.ToString() });
    static object? Ext(Entity e) { try { var x = e.GeometricExtents; return new[] { x.MinPoint.X, x.MinPoint.Y, x.MaxPoint.X, x.MaxPoint.Y }; } catch { return null; } }

    static ObjectId PaperId(Transaction tr, Database db)
    {
        var d = (DBDictionary)tr.GetObject(db.LayoutDictionaryId, OpenMode.ForRead);
        if (!d.Contains(LayoutName)) throw new InvalidOperationException("Layout not found: " + LayoutName);
        return ((Layout)tr.GetObject(d.GetAt(LayoutName), OpenMode.ForRead)).BlockTableRecordId;
    }
    static string BlockName(Transaction tr, BlockReference r) => ((BlockTableRecord)tr.GetObject(r.BlockTableRecord, OpenMode.ForRead)).Name;
    static void SaveNew(Database db, string output)
    {
        if (File.Exists(output)) throw new InvalidOperationException("Output exists: " + output);
        db.SaveAs(output, DwgVersion.Current);
    }

    [CommandMethod("DTINSPECT")]
    public void Inspect()
    {
        var db = Db; var output = Env("DT_REPORT");
        var layouts = new List<object>(); var blocks = new List<object>();
        using (var tr = db.TransactionManager.StartTransaction())
        {
            var bt = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForRead);
            foreach (ObjectId btid in bt)
            {
                var b = (BlockTableRecord)tr.GetObject(btid, OpenMode.ForRead);
                if (!b.IsLayout)
                {
                    if (b.Name.StartsWith("A$C") || b.Name.StartsWith("DT_FRAME_"))
                    {
                        var items = new List<object>();
                        foreach (ObjectId eid in b)
                            if (tr.GetObject(eid, OpenMode.ForRead) is Entity ee)
                                items.Add(new { handle = ee.Handle.ToString(), type = ee.GetType().Name, layer = ee.Layer, extent = Ext(ee), text = ee switch { DBText t => t.TextString, MText m => m.Contents, _ => null } });
                        blocks.Add(new { name = b.Name, items });
                    }
                    continue;
                }
                var lo = (Layout)tr.GetObject(b.LayoutId, OpenMode.ForRead);
                var ents = new List<object>();
                foreach (ObjectId id in b)
                {
                    if (tr.GetObject(id, OpenMode.ForRead) is not Entity e) continue;
                    string? text = e switch { DBText t => t.TextString, MText m => m.Contents, Dimension d => d.DimensionText, _ => null };
                    string? block = null; List<object>? attrs = null; object? vp = null;
                    if (e is BlockReference br)
                    {
                        block = BlockName(tr, br); attrs = new();
                        foreach (ObjectId ai in br.AttributeCollection)
                            if (tr.GetObject(ai, OpenMode.ForRead) is AttributeReference a) attrs.Add(new { a.Tag, a.TextString, handle = a.Handle.ToString() });
                    }
                    if (e is Viewport v) vp = new { v.Number, v.CustomScale, v.Locked, v.Width, v.Height, Center = new[] { v.CenterPoint.X, v.CenterPoint.Y }, ViewCenter = new[] { v.ViewCenter.X, v.ViewCenter.Y } };
                    ents.Add(new { handle = e.Handle.ToString(), type = e.GetType().Name, layer = e.Layer, extent = Ext(e), text = text?.Substring(0, Math.Min(text.Length, 300)), block, attrs, vp });
                }
                layouts.Add(new { name = lo.LayoutName, lo.ModelType, lo.CanonicalMediaName, entities = ents });
            }
            tr.Commit();
        }
        Write(output, new { filename = db.Filename, layouts, blocks });
    }

    [CommandMethod("DTPROBE")]
    public void Probe()
    {
        var db = Db; var rows = new List<object>();
        using (var tr = db.TransactionManager.StartTransaction())
        {
            var paper = (BlockTableRecord)tr.GetObject(PaperId(tr, db), OpenMode.ForRead);
            foreach (ObjectId id in paper)
            {
                if (tr.GetObject(id, OpenMode.ForRead) is not BlockReference r || !BlockName(tr, r).StartsWith("A$C")) continue;
                var es = new DBObjectCollection(); r.Explode(es);   // A$C only; never HYPERSTEELPAGEHEADER
                foreach (Entity e in es)
                {
                    if (e is DBText t) { var x = t.GeometricExtents; rows.Add(new { t.TextString, frame = r.Handle.ToString(), pos = new[] { t.Position.X, t.Position.Y }, t.Height, extent = new[] { x.MinPoint.X, x.MinPoint.Y, x.MaxPoint.X, x.MaxPoint.Y } }); }
                    e.Dispose();
                }
            }
            tr.Commit();
        }
        Write(Env("DT_REPORT"), rows);
    }

    [CommandMethod("DTAPPLY")]
    public void Apply()
    {
        var job = JsonSerializer.Deserialize<ApplyJob>(File.ReadAllText(Env("DT_JOB")))!;
        try
        {
            var db = Db; var erased = new List<string>(); ObjectId paperId;
            var numberPos = job.NumberPos ?? throw new InvalidOperationException("NumberPos required (x,y,height,width) — measure it on the donor frame");
            using (var tr = db.TransactionManager.StartTransaction())
            {
                paperId = PaperId(tr, db);
                foreach (var h in job.Erase)
                {
                    var e = (Entity)tr.GetObject(db.GetObjectId(false, new Handle(Convert.ToInt64(h, 16)), 0), OpenMode.ForWrite);
                    if (e.OwnerId != paperId) throw new InvalidOperationException("Erase target outside paper layout: " + h);
                    e.Erase(); erased.Add(h);
                }
                tr.Commit();
            }
            using var donor = new Database(false, true);
            donor.ReadDwgFile(job.Donor, FileShare.Read, true, ""); donor.CloseInput(true);
            var seed = new List<Entity>();
            using (var tr = donor.TransactionManager.StartTransaction())
            {
                var paper = (BlockTableRecord)tr.GetObject(PaperId(tr, donor), OpenMode.ForRead);
                foreach (ObjectId id in paper)
                    if (tr.GetObject(id, OpenMode.ForRead) is BlockReference r && BlockName(tr, r).StartsWith("A$C"))
                    { var es = new DBObjectCollection(); r.Explode(es); foreach (Entity e in es) seed.Add(e); }
                if (seed.Count < job.MinDonorEntities) throw new InvalidOperationException($"Donor frame has {seed.Count} entities (< {job.MinDonorEntities})");
                tr.Commit();
            }
            using (var tr = db.TransactionManager.StartTransaction())
            {
                var bt = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForWrite);
                var paper = (BlockTableRecord)tr.GetObject(paperId, OpenMode.ForWrite);
                var lt = (LayerTable)tr.GetObject(db.LayerTableId, OpenMode.ForWrite);
                if (!lt.Has(job.NumberLayer)) { var lr = new LayerTableRecord { Name = job.NumberLayer }; lt.Add(lr); tr.AddNewlyCreatedDBObject(lr, true); }
                foreach (var pg in job.Pages)
                {
                    var block = new BlockTableRecord { Name = "DT_FRAME_" + pg.Number.Replace('-', '_') };
                    bt.Add(block); tr.AddNewlyCreatedDBObject(block, true);
                    int titles = 0, scales = 0;
                    foreach (var original in seed)
                    {
                        var e = (Entity)original.Clone(); var color = e.Color; var lw = e.LineWeight;
                        e.SetDatabaseDefaults(db); e.Color = color; e.LineWeight = lw; e.LayerId = db.LayerZero;
                        if (e is DBText t)
                        {
                            t.TextStyleId = db.Textstyle;
                            if (t.TextString == job.DonorTitleText) { t.TextString = pg.Title; t.WidthFactor = 0.9; titles++; }
                            if (t.TextString == job.DonorScaleText)
                            {
                                t.TextString = job.ScalePrefix + (pg.Scale ?? job.ScaleFallback); scales++;
                                if (t.TextString.Length > 6) t.WidthFactor = 0.75;   // long scale strings overrun the next cell
                            }
                        }
                        // Move the info band with ShiftY; stretch only the vertical border segments that cross it.
                        var ex = e.GeometricExtents;
                        if (ex.MaxPoint.Y <= job.BottomBandY + 0.01) e.TransformBy(Matrix3d.Displacement(new Vector3d(0, pg.ShiftY, 0)));
                        else if (ex.MinPoint.Y < job.BottomBandY && pg.ShiftY != 0)
                        {
                            if (e is Line ln) { if (ln.StartPoint.Y <= job.BottomBandY) ln.StartPoint += new Vector3d(0, pg.ShiftY, 0); if (ln.EndPoint.Y <= job.BottomBandY) ln.EndPoint += new Vector3d(0, pg.ShiftY, 0); }
                            else if (e is Polyline pl) { for (int i = 0; i < pl.NumberOfVertices; i++) { var p = pl.GetPoint2dAt(i); if (p.Y <= job.BottomBandY) pl.SetPointAt(i, new Point2d(p.X, p.Y + pg.ShiftY)); } }
                            else throw new InvalidOperationException("Unclassified frame entity crossing the info band: " + e.GetType().Name);
                        }
                        block.AppendEntity(e); tr.AddNewlyCreatedDBObject(e, true);
                    }
                    if (titles != 1) throw new InvalidOperationException($"Donor title text '{job.DonorTitleText}' found {titles} times (expected 1)");
                    if (scales != 1) throw new InvalidOperationException($"Donor scale text '{job.DonorScaleText}' found {scales} times (expected 1)");
                    var num = new DBText { TextString = pg.Number, Position = new Point3d(numberPos[0], numberPos[1] + pg.ShiftY, 0), Height = numberPos[2], WidthFactor = numberPos.Length > 3 ? numberPos[3] : 1, TextStyleId = db.Textstyle };
                    block.AppendEntity(num); tr.AddNewlyCreatedDBObject(num, true);
                    var br = new BlockReference(new Point3d(pg.X, 0, 0), block.ObjectId);
                    paper.AppendEntity(br); tr.AddNewlyCreatedDBObject(br, true);
                    // Marker on a dedicated layer lets the checker count pages; it is plotted only if MarkPos is given.
                    var m = job.MarkPos;
                    var mark = new DBText { TextString = pg.Number, Position = new Point3d(pg.X + (m?[0] ?? 0), m?[1] ?? 0, 0), Height = m?[2] ?? 0.01, Layer = job.NumberLayer, ColorIndex = 1, Visible = m != null };
                    paper.AppendEntity(mark); tr.AddNewlyCreatedDBObject(mark, true);
                }
                tr.Commit();
            }
            foreach (var e in seed) e.Dispose();
            SaveNew(db, job.Output);
            lastApplied = job.Output;
            Write(job.Report, new { success = true, job.Output, erased, pages = job.Pages });
        }
        catch (System.Exception ex) { Fail(job.Report, ex); }
    }

    [CommandMethod("DTCOVER")]
    public void Cover()
    {
        string output = Env("DT_OUTPUT"), report = Env("DT_REPORT"), from = Env("DT_FROM"), to = Env("DT_TO");
        int expect = int.Parse(EnvOr("DT_EXPECT_COUNT", "0"));
        try
        {
            var db = Db; int n = 0;
            using (var tr = db.TransactionManager.StartTransaction())
            {
                var p = (BlockTableRecord)tr.GetObject(PaperId(tr, db), OpenMode.ForRead);
                foreach (ObjectId id in p)
                {
                    if (tr.GetObject(id, OpenMode.ForRead) is MText t && t.Contents.Contains(from)) { t.UpgradeOpen(); t.Contents = t.Contents.Replace(from, to); n++; }
                    else if (tr.GetObject(id, OpenMode.ForRead) is DBText d && d.TextString.Contains(from)) { d.UpgradeOpen(); d.TextString = d.TextString.Replace(from, to); n++; }
                }
                if (n == 0 || (expect > 0 && n != expect)) throw new InvalidOperationException($"Cover text count {n} (expected {(expect > 0 ? expect : ">0")})");
                tr.Commit();
            }
            SaveNew(db, output);
            Write(report, new { success = true, changed = n, output });
        }
        catch (System.Exception ex) { Fail(report, ex); }
    }

    [CommandMethod("DTINDEX")]
    public void Index()
    {
        var job = JsonSerializer.Deserialize<IndexJob>(File.ReadAllText(Env("DT_INDEX_JOB")))!;
        try
        {
            // Core Console does not update db.Filename after SaveAs, so DTAPPLY records its success here.
            if (lastApplied == null || !string.Equals(Path.GetFullPath(lastApplied), Path.GetFullPath(job.Output), StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException("DTINDEX must follow a successful DTAPPLY to the same Output in this session");
            var rows = JsonSerializer.Deserialize<IndexRow[]>(File.ReadAllText(job.RowsFile))!;
            if (rows.Length > job.MaxRows) throw new InvalidOperationException($"{rows.Length} rows > MaxRows {job.MaxRows}; split into more index pages");
            var hd = job.Headers ?? new[] { "圖號", "分類", "圖名", "頁次" };
            var db = Db;
            using (var tr = db.TransactionManager.StartTransaction())
            {
                var b = (BlockTableRecord)tr.GetObject(PaperId(tr, db), OpenMode.ForWrite);
                var st = (TextStyleTable)tr.GetObject(db.TextStyleTableId, OpenMode.ForWrite);
                ObjectId style;
                if (st.Has("DT_INDEX")) style = st["DT_INDEX"];
                else { var rec = new TextStyleTableRecord { Name = "DT_INDEX", FileName = job.FontFile }; style = st.Add(rec); tr.AddNewlyCreatedDBObject(rec, true); }
                void Add(Entity e) { b.AppendEntity(e); tr.AddNewlyCreatedDBObject(e, true); }
                void Text(double x, double y, string s, double h = 3) => Add(new DBText { TextString = s, Position = new Point3d(x, y, 0), Height = h, TextStyleId = style });
                void Ln(double x1, double y1, double x2, double y2) => Add(new Line(new Point3d(x1, y1, 0), new Point3d(x2, y2, 0)));
                Text(14, 255, job.Title, 6); if (job.Subtitle != "") Text(14, 245, job.Subtitle, 3.2);
                double top = 236, step = 10, bottom = top - step * (rows.Length + 1);
                double[] cols = { 14, 64, 102, 355, 393 };
                foreach (double x in cols) Ln(x, top, x, bottom);
                for (int i = 0; i <= rows.Length + 1; i++) Ln(14, top - step * i, 393, top - step * i);
                Text(18, top - 7, hd[0], 3.2); Text(69, top - 7, hd[1], 3.2); Text(107, top - 7, hd[2], 3.2); Text(361, top - 7, hd[3], 3.2);
                for (int i = 0; i < rows.Length; i++)
                {
                    double y = top - step * (i + 1) - 7;
                    Text(18, y, rows[i].Number); Text(69, y, rows[i].Category); Text(107, y, rows[i].Title); Text(361, y, rows[i].BookPage.ToString("00"));
                }
                tr.Commit();
            }
            db.SaveAs(job.Output, DwgVersion.Current);   // overwrites the DTAPPLY output only (checked above)
            Write(job.Report, new { success = true, rows = rows.Length, job.Output });
        }
        catch (System.Exception ex) { Fail(job.Report, ex); }
    }

    [CommandMethod("DTPLOTALL")]
    public void PlotAll()
    {
        var plots = JsonSerializer.Deserialize<JsonElement[]>(Env("DT_PLOTS"))!;
        foreach (var p in plots) PlotOne(p.GetProperty("Pdf").GetString()!, p.GetProperty("Report").GetString()!, JsonSerializer.Deserialize<double[]>(p.GetProperty("Window").GetRawText())!);
    }

    static void PlotOne(string pdf, string report, double[] win)
    {
        try
        {
            var doc = Application.DocumentManager.MdiActiveDocument; var db = doc.Database; ObjectId li;
            using (var tr = db.TransactionManager.StartTransaction()) { li = ((DBDictionary)tr.GetObject(db.LayoutDictionaryId, OpenMode.ForRead)).GetAt(LayoutName); tr.Commit(); }
            LayoutManager.Current.CurrentLayout = LayoutName;
            using var ps = new PlotSettings(false);
            using (var tr = db.TransactionManager.StartTransaction()) { ps.CopyFrom((Layout)tr.GetObject(li, OpenMode.ForRead)); tr.Commit(); }
            var v = PlotSettingsValidator.Current;
            v.SetPlotConfigurationName(ps, EnvOr("DT_PC3", "DWG To PDF.pc3"), EnvOr("DT_MEDIA", "ISO_full_bleed_A3_(420.00_x_297.00_MM)"));
            v.RefreshLists(ps);
            v.SetPlotWindowArea(ps, new Extents2d(new Point2d(win[0], win[1]), new Point2d(win[2], win[3])));
            v.SetPlotType(ps, Autodesk.AutoCAD.DatabaseServices.PlotType.Window);
            v.SetUseStandardScale(ps, true); v.SetStdScaleType(ps, StdScaleType.ScaleToFit);
            v.SetPlotCentered(ps, true); v.SetPlotRotation(ps, PlotRotation.Degrees000);
            var pi = new PlotInfo { Layout = li, OverrideSettings = ps };
            new PlotInfoValidator { MediaMatchingPolicy = MatchingPolicy.MatchEnabled }.Validate(pi);
            if (File.Exists(pdf)) throw new InvalidOperationException("PDF exists");
            using var eng = PlotFactory.CreatePublishEngine();
            using var pd = new PlotProgressDialog(false, 1, true);
            eng.BeginPlot(pd, null); eng.BeginDocument(pi, doc.Name, null, 1, true, pdf);
            using (var page = new PlotPageInfo()) { eng.BeginPage(page, pi, true, null); eng.BeginGenerateGraphics(null); eng.EndGenerateGraphics(null); eng.EndPage(null); }
            eng.EndDocument(null); eng.EndPlot(null);
            if (!File.Exists(pdf) || new FileInfo(pdf).Length < 1000) throw new InvalidOperationException("PDF missing or empty");
            Write(report, new { success = true, pdf, window = win, media = ps.CanonicalMediaName });
        }
        catch (System.Exception ex) { Fail(report, ex); }
    }

    [CommandMethod("DTCHECKFRAME")]
    public void CheckFrame()
    {
        var db = Db; var rows = new List<object>();
        using (var tr = db.TransactionManager.StartTransaction())
        {
            var p = (BlockTableRecord)tr.GetObject(PaperId(tr, db), OpenMode.ForRead);
            foreach (ObjectId id in p)
            {
                if (tr.GetObject(id, OpenMode.ForRead) is not BlockReference r) continue;
                var d = (BlockTableRecord)tr.GetObject(r.BlockTableRecord, OpenMode.ForRead);
                if (!d.Name.StartsWith("DT_FRAME_")) continue;
                var texts = new List<object>();
                foreach (ObjectId eid in d)
                    if (tr.GetObject(eid, OpenMode.ForRead) is DBText t) { var ex = t.GeometricExtents; ex.TransformBy(r.BlockTransform); texts.Add(new { text = t.TextString, extent = new[] { ex.MinPoint.X, ex.MinPoint.Y, ex.MaxPoint.X, ex.MaxPoint.Y }, height = t.Height, width = t.WidthFactor }); }
                var be = r.GeometricExtents;
                rows.Add(new { block = d.Name, extent = new[] { be.MinPoint.X, be.MinPoint.Y, be.MaxPoint.X, be.MaxPoint.Y }, texts });
            }
            tr.Commit();
        }
        Write(Env("DT_REPORT"), rows);
    }

    static IEnumerable<(BlockReference r, AttributeReference a)> Attrs(Transaction tr, Database db, string block, string? tag)
    {
        var p = (BlockTableRecord)tr.GetObject(PaperId(tr, db), OpenMode.ForRead);
        foreach (ObjectId id in p)
        {
            if (tr.GetObject(id, OpenMode.ForRead) is not BlockReference r || BlockName(tr, r) != block) continue;
            foreach (ObjectId ai in r.AttributeCollection)
                if (tr.GetObject(ai, OpenMode.ForRead) is AttributeReference a && (tag == null || a.Tag == tag)) yield return (r, a);
        }
    }

    [CommandMethod("DTATTRREAD")]
    public void AttrRead()
    {
        var db = Db; var rows = new List<object>();
        using (var tr = db.TransactionManager.StartTransaction())
        {
            foreach (var (r, a) in Attrs(tr, db, EnvOr("DT_BLOCK", "HYPERSTEELPAGEHEADER"), null).ToList())
                rows.Add(new { insert = new[] { r.Position.X, r.Position.Y }, a.Tag, a.TextString, a.Height, a.WidthFactor, just = a.Justify.ToString(), pos = new[] { a.Position.X, a.Position.Y }, align = new[] { a.AlignmentPoint.X, a.AlignmentPoint.Y }, style = ((TextStyleTableRecord)tr.GetObject(a.TextStyleId, OpenMode.ForRead)).Name });
            tr.Commit();
        }
        Write(Env("DT_REPORT"), rows);
    }

    [CommandMethod("DTSETATTR")]
    public void SetAttr()
    {
        string output = Env("DT_OUTPUT"), report = Env("DT_REPORT"), block = Env("DT_BLOCK"), tag = Env("DT_TAG"), from = EnvOr("DT_FROM", ""), to = Env("DT_TO");
        try
        {
            var db = Db; var changed = new List<object>();
            using (var tr = db.TransactionManager.StartTransaction())
            {
                foreach (var (_, a) in Attrs(tr, db, block, tag).ToList())
                {
                    if (a.TextString != from) throw new InvalidOperationException($"Unexpected value '{a.TextString}' (expected '{from}')");
                    a.UpgradeOpen(); a.TextString = to; changed.Add(new { handle = a.Handle.ToString(), old = from, value = to });
                }
                if (changed.Count != 1) throw new InvalidOperationException("Expected 1 attribute, got " + changed.Count);
                tr.Commit();
            }
            SaveNew(db, output);
            Write(report, new { success = true, changed, output });
        }
        catch (System.Exception ex) { Fail(report, ex); }
    }

    // blank -> filled; already NAME -> refit (height/position only); other value -> kept_other (untouched, still saved)
    [CommandMethod("DTPROJFILL")]
    public void ProjFill()
    {
        string output = Env("DT_OUTPUT"), report = Env("DT_REPORT"), name = Env("DT_NAME");
        string block = EnvOr("DT_BLOCK", "HYPERSTEELPAGEHEADER"), tag = EnvOr("DT_TAG", "PROJECT");
        double h = EnvD("DT_HEIGHT"), ay = EnvD("DT_ALIGNY");
        try
        {
            var db = Db; var changed = new List<object>(); string action = "";
            using (var tr = db.TransactionManager.StartTransaction())
            {
                foreach (var (_, a) in Attrs(tr, db, block, tag).ToList())
                {
                    var old = a.TextString;
                    if (old != "" && old != name) { action = "kept_other:" + old; changed.Add(new { handle = a.Handle.ToString(), old }); continue; }
                    a.UpgradeOpen(); a.TextString = name; a.Height = h;
                    a.TransformBy(Matrix3d.Displacement(new Vector3d(0, ay - a.AlignmentPoint.Y, 0)));
                    if (a.Justify != AttachmentPoint.BaseLeft) a.AdjustAlignment(db);
                    action = old == "" ? "filled" : "refit";
                    changed.Add(new { handle = a.Handle.ToString(), old, a.Height, alignY = a.AlignmentPoint.Y });
                }
                if (changed.Count != 1) throw new InvalidOperationException($"Expected 1 {tag}, got {changed.Count}");
                tr.Commit();
            }
            SaveNew(db, output);
            Write(report, new { success = true, action, changed, output });
        }
        catch (System.Exception ex) { Fail(report, ex); }
    }
}
