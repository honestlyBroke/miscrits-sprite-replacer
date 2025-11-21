extends SceneTree

func _init() -> void:
    var args: PackedStringArray = OS.get_cmdline_user_args()
    if args.size() < 2:
        push_error("Usage: godot --headless --script crits_single_decode.gd -- <ENCRYPTED_IN> <PNG_OUT>")
        quit()
        return

    var in_path: String = args[0]
    var out_path: String = args[1]

    # Load raw encrypted bytes
    var f: FileAccess = FileAccess.open(in_path, FileAccess.READ)
    if f == null:
        push_error("Cannot open encrypted file: " + in_path)
        quit()
        return

    var bytes: PackedByteArray = f.get_var(true)
    f.close()

    if bytes.size() < 8:
        push_error("Encrypted file too small: " + in_path)
        quit()
        return

    var img: Image = Image.new()
    var err: int = ERR_CANT_OPEN

    # Detect PNG by magic number
    if bytes[0] == 0x89 and bytes[1] == 0x50 and bytes[2] == 0x4E and bytes[3] == 0x47:
        err = img.load_png_from_buffer(bytes)
    # Detect JPG
    elif bytes[0] == 0xFF and bytes[1] == 0xD8:
        err = img.load_jpg_from_buffer(bytes)
    else:
        push_error("Unknown image format for: " + in_path)
        quit()
        return

    if err != OK:
        push_error("Failed to decode: " + in_path + " (error %d)" % err)
        quit()
        return

    # Ensure output directory exists
    var dir_path: String = out_path.get_base_dir()
    if dir_path != "":
        DirAccess.make_dir_recursive_absolute(dir_path)

    err = img.save_png(out_path)
    if err != OK:
        push_error("Failed to save PNG: " + out_path)
    else:
        print("Decoded to: " + out_path)

    quit()
