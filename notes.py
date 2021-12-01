# notes.py: handles reading and writing notes
import sys  # for exiting
import argparse  # for argument parsing
from pathlib import Path  # for file exists checking
import os  # used to rename files
import datetime  # used to get timestamp formats

settings = {}


# load_settings(): read the ./settings file into the settings variable
def load_settings():
    global settings  # global because we are writing to the global settings variable
    with open("settings", "r") as f:  # open the settings file
        for line in f.readlines():  # read the lines
            line = line.split("=")  # split each line by "="
            if len(line) == 2:  # if the line is a valid key/pair, set the setting
                key = line[0].strip()  # remove the excess spaces
                val = line[1].strip()  # remove the excess spaces
                settings[key] = val  # store as a key/val pair
    return


# write_settings(): write the settings variable into the ./settings file
def write_settings(_settings):
    with open("settings", "w") as f:  # open the settings file
        for key in _settings:
            line = key + "=" + _settings[key] + "\n"
            f.write(line)
    return


# sanitize_notebook(): strips non-alphanumerics from notebook
def sanitize(notebook):
    return ''.join(filter(str.isalnum, notebook))


# get_long_time(): gets the current datetime in the format day month, year @ hour:min
def get_long_time():
    return datetime.datetime().strftime("%d %B, %Y @ %H:%M")


# get_log_time(): gets the current datetime in the format day-month-year hour:min
def get_log_time():
    return datetime.datetime.now().strftime("%d %B %Y @ %H:%M")


# record(): records a string to a given file
def record(notebook, text):
    # open the file
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "notebooks", notebook), "a") as f:
        # log the text
        f.write("[" + get_log_time() + "] " + text + "\n")
    return


# boolean check for if a notebook already exists. deleted: whether to check deleted notebook instead of active; error: whether to print an error if the notebook is not found.
def check_notebook_exists(notebook, deleted=False, error=False):
    # check if given notebook exists
    if not deleted and Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "notebooks", sanitize(notebook))).is_file():
        return True
    # check if a deleted notebook exists
    elif deleted and Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "notebooks", "." + sanitize(notebook))).is_file():
        return True
    else:
        if error:
            print("Notebook", notebook, "does not exist! Use --new to create it, or --list to list all notebooks")
            sys.exit()
        return False


# checks if an argument was specified, if not, asks for a notebook
def check_notebook_argument(arg):
    print(">", arg)
    if arg == "":
        notebooks = list_notebooks()  # output all notebooks
        while arg is None:
            arg = input("Specify a notebook: ")  # ask user to specify a notebook
            if arg not in notebooks:
                print("Notebook does not exist, or has been deleted.")
    return arg


# create_notebook(): creates a notebook
def create_notebook(notebook):
    # check if notebook already exists
    if check_notebook_exists(notebook):
        print("Notebook already exists! Delete it by using --delete, or rename it by using --rename")
        return
    
    # check if notebook was deleted
    if check_notebook_exists("." + notebook):
        # ask if user wants to restore the deleted notebook
        response = input("Notebook " + notebook + " has been deleted, do you want to restore the deleted notebook? (yes/no)" )
        if response == "yes":
            # rename the deleted notebook
            os.rename(os.path.join(os.path.dirname(os.path.abspath(__file__)), "notebooks", "." + notebook), os.path.join(os.path.dirname(os.path.abspath(__file__)), "notebooks", notebook))
            print("Restored notebook", notebook)
            return
        if response == "no":
            # create the new notebook
            print("Will not restore the deleted notebook", notebook, "(you can still restore it using --restore until you delete this new notebook)")
            return

    print("Creating notebook", notebook)

    # create the notebook and log the notebook creation
    record(notebook, "Notebook Created!")
    return


# delete_notebook(): renames a notebook to delete it
def delete_notebook(notebook):
    # check if the notebook exists
    check_notebook_exists(notebook, error=True)

    # check if there is a deleted notebook
    if check_notebook_exists(notebook, deleted=True):
        print("Deleted notebook already exists for", notebook )
        confirm = input("Do you wish to overwrite it? (yes/no) ")
        if confirm == "yes":
            print("Overwriting deleted notebook", notebook)
        else:
            return

    os.rename(os.path.join(os.path.dirname(os.path.abspath(__file__)), "notebooks", notebook), os.path.join(os.path.dirname(os.path.abspath(__file__)), "notebooks", "." + notebook))
    print("Notebook", notebook, "deleted!")
    print("(you can restore it using --restore)")
    return


# restore_notebook(): renames a deleted notebook to restore it
def restore_notebook(notebook):
    # check if the deleted notebook exists
    check_notebook_exists(notebook, deleted=True, error=True)
    
    # check if there is a current notebook
    if check_notebook_exists(notebook):
        print("Notebook already exists for", notebook )
        confirm = input("Do you wish to overwrite it? (yes/no) ")
        if confirm == "yes":
            print("Overwriting notebook", notebook)
        else:
            print("Confirmation rejected")
            return

    os.rename(os.path.join(os.path.dirname(os.path.abspath(__file__)), "notebooks", "." + notebook), os.path.join(os.path.dirname(os.path.abspath(__file__)), "notebooks", notebook))
    print("Notebook", notebook, "restored!")
    return


# show_notes(): shows a given number of last lines from a notebook
def show_notes(notebook, n):
    # open the notebook
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "notebooks", notebook), "r") as f:
        # read the lines from the notebook
        notes = f.readlines()
        # show the most recent n lines, or all lines if n = -1
        for note in notes[(-1 * int(n) if int(n) > 0 else 0):]:
            print(note.replace("\n", ""))  # show the note, but filter out the newline (since print() adds a newline)
    return


# write_note(): asks for and writes a note to a notebook
def write_note(notebook):
    print("** Notebook:", notebook, "**")
    print("Use ^C to exit")

    # check if notebook exists
    if not check_notebook_exists(notebook):
        print("Notebook does not exist! Create a notebook by using --new")
        return
    
    # show the last settings:num_recent_notes notes
    show_notes(notebook, settings["num_recent_notes"])

    # ask the user to input a note
    try:
        while True:
            note = input("> ")
            record(notebook, note.replace("\n", ""))
            show_notes(notebook, 1)
    except KeyboardInterrupt:
        print("Closing notebook")
    
    return


# list_notebooks(): lists all notebook names
def list_notebooks(deleted=False, header=""):
    all_notebooks = os.listdir("notebooks")  # get all notebooks
    active_notebooks = [x for x in all_notebooks if x[0] != "."]  # pull the active notebooks
    deleted_notebooks = [x[1:] for x in all_notebooks if x[0] == "."]  # pull the deleted notebooks, [1:] to remove the preceeding . in the file name
    notebooks = active_notebooks if not deleted else deleted_notebooks  # set the notebooks to list to either active or deleted

    if len(notebooks) == 0:
        print("No " + (header.lower() + " " if header else "") + "notebooks found!")
        return notebooks

    # output the notebook names
    print("** " + (header.capitalize() + " " if header else "") + "Notebooks **")
    for notebook in notebooks:
        print(" ~", notebook)        

    return notebooks


# rename_notebook(): renames a notebook
def rename_notebook(from_notebook, to_notebook):
    # check if the renaming notebook exists
    check_notebook_exists(from_notebook, error=True)

    # rename the notebook
    os.rename(os.path.join(os.path.dirname(os.path.abspath(__file__)), "notebooks", from_notebook), os.path.join(os.path.dirname(os.path.abspath(__file__)), "notebooks", to_notebook))
    print("Renamed notebook " + from_notebook + " to " + to_notebook)
    return


# process the command to add, edit, or delete notes
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple terminal-based notes utility! Use no arguments to get started using the default notebook, or --new [string] to create a new notebook.")  # Instantiate the parser

    parser.add_argument("--new", "--create", "-n", type=str, nargs=1, help="Create a new notebook.")  # done
    parser.add_argument("--write", "-w", type=str, nargs=1, help="Open a notebook for writing.")  # done
    parser.add_argument("--default", type=str, nargs=1, help="The notebook to set as the default note.")  # done
    parser.add_argument("--delete", type=str, nargs=1, help="The notebook to delete. The actual notebook data will not be deleted, but you will no longer be able to write to it unless you --restore it.")  # done
    parser.add_argument("--restore", type=str, nargs=1, help="Restore a deleted notebook, use --listall to show all deleted notebooks.")  # done
    parser.add_argument("--rename", type=str, nargs=2, help="Rename a notebook.")  # done
    parser.add_argument("--show", "-s", "-d", type=str, nargs=1, help="Show the contents of a given notebook, default to all notes, use the -c flag to specify a specific number of lines.")  # done
    parser.add_argument("-c", type=int, nargs=1, help="Used in conjunction with the --show command to indicate the number of lines to show.")
    parser.add_argument("--listall", "-la", action="store_true", help="List all notebooks, including deleted notebooks.")  # done
    parser.add_argument("--list", "-l", action="store_true", help="List active notebooks.")  # done

    args = parser.parse_args()

    # load the settings
    load_settings()
    count = settings["default_note_count"]
    notebook = settings["default_notebook"]

    # create a new notebook
    if args.new:
        create_notebook(sanitize(args.new[0]))
        
    # delete a notebook
    if args.delete:
        delete_notebook(sanitize(args.delete[0]))

    # restore a notebook
    if args.restore:
        restore_notebook(args.restore[0])

    # set the number of recent lines to show
    if args.c:
        count = args.c[0]

    # list all notebooks
    if args.list:
        list_notebooks()

    # list all deleted notebooks
    if args.listall:
        list_notebooks(header="Active")
        print()
        list_notebooks(deleted=True, header="Deleted")
    
    # show notebook contents
    if args.show:
        check_notebook_exists(args.show[0], error=True)
        print("** Notebook:", sanitize(args.show[0]), "**")
        show_notes(sanitize(args.show[0]), count)

    # set a default notebook
    if args.default:
        notebook = args.default[0]
        check_notebook_exists(notebook, error=True)
        settings["default_notebook"] = notebook
        write_settings(settings)
        print("Set default notebook to", notebook)

    # write to a specified notebook
    if args.write:
        check_notebook_exists(args.write[0], error=True)
        write_note(args.write[0])
        
    # rename a notebook
    if args.rename:
        # parse the arguments
        from_notebook = sanitize(args.rename[0])
        to_notebook = sanitize(args.rename[1])

        # rename the notebook
        rename_notebook(from_notebook, to_notebook)        

    # write to the default notebook
    if len(sys.argv) <= 1:
        print("Opening default notebook, \"" + settings["default_notebook"] + "\"")
        write_note(settings["default_notebook"])
