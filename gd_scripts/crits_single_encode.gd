extends SceneTree

func _init() -> void:
    var args: PackedStringArray = OS.get_cmdline_user_args()
    if args.size() < 2:
        push_error("Usage: godot --headless --script crits_single_encode.gd -- <PNG_IN> <ENCRYPTED_OUT>")
        quit()
        return

    var image_path: String = args[0]
    var cache_path: String = args[1]

    _encode_one(image_path, cache_path)
    quit()

func _encode_one(image_path: String, cache_path: String) -> void:
    var img: Image = Image.new()
    var err: int = img.load(image_path)
    if err != OK:
        push_error("Failed to load image: " + image_path + " (error code " + str(err) + ")")
        return

    var ext: String = image_path.get_extension().to_lower()
    var bytes: PackedByteArray = PackedByteArray()

    if ext == "png":
        bytes = img.save_png_to_buffer()
    elif ext == "jpg" or ext == "jpeg":
        bytes = img.save_jpg_to_buffer()
    else:
        # Default to PNG if extension unknown
        bytes = img.save_png_to_buffer()

    if bytes.is_empty():
        push_error("Could not encode image: " + image_path)
        return

    var dir_path: String = cache_path.get_base_dir()
    if dir_path != "":
        DirAccess.make_dir_recursive_absolute(dir_path)

    var f: FileAccess = FileAccess.open(cache_path, FileAccess.WRITE)
    if f == null:
        push_error("Cannot write cache file: " + cache_path)
        return

    # Store PNG/JPG bytes as PackedByteArray (same format the game uses)
    f.store_var(bytes, true)
    f.close()

    print("Encoded and wrote cache file: " + cache_path)
