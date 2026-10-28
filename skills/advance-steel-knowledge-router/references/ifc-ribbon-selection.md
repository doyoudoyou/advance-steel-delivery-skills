# Advance Steel IFC Ribbon selection

Capture SelectImplied and immutable ObjectId[] before ExecuteInCommandContextAsync: switching from application/Ribbon context can clear PickFirst. In callback verify the same active document and valid non-erased IDs belonging to that database, then restore only the captured implied selection before invoking export. Empty selection must return without publication. Test through the actual Ribbon ICommand, not only the registered CommandMethod: command-line success does not prove Ribbon selection survives context switching.

Resolve AutoCAD ByLayer/ByAci via the resolved Autodesk Color.ColorValue RGB, not raw Red/Green/Blue (observed ACI 21 raw channels zero while ColorValue and independent COM report 255,159,127).

Read IFC2X3 GlobalId as field or property then underlying STRING.Value, not ToString() which returns quoted STEP serialization. Verify exact 22-character IFC GUID before matching. Preserve source ASId from the native object rather than inventing it from marks.

Use extended Windows paths for Python IFC/evidence I/O and long-path cleanup. Windows CreateProcess may still reject a long executable path: stage executable packages under bounded paths, but retain >260-character data-path regression tests. Freeze setuptools vendored backports.tarfile when required by PyInstaller pkg_resources runtime hook, and execute the final copied bundle's EXE rather than just the temporary build-tree EXE.
