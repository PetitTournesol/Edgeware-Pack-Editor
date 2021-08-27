import os, pathlib, json, shutil, zipfile
from tkinter.constants import RAISED
from tkinter import *
from tkinter.ttk import *
from tkinter import Tk, ttk, simpledialog, filedialog, messagebox

PATH = str(pathlib.Path(__file__).parent.absolute())
os.chdir(PATH)

LOCAL_VERSION = '1.0.0'

JSON_FILE_NAMES = ['web', 'prompt', 'captions']
NONJSON_FILE_NAMES = ['discord.dat']
MEDIA_TYPES  = ['aud', 'img', 'vid']
WALL_FILE_TYPES = ['jpg', 'jpeg', 'png']
EXCLUDED_TREE_OPTS = ['minLen', 'maxLen', 'subtext']

hasBeenSaved = False
heldSavePath = ''

class Pack:
    def __init__(self):
        self.name = 'Unnamed Edgeware Pack'

        #default assets
        
        self.defaultWebList        = {'urls':['https://www.google.com/'], 'args':['']}
        self.defaultCaptionList    = {'prefix':[], 'default':[], 'subtext':'I Submit <3'}
        self.defaultPromptList     = {'moods':['default'], 'subtext':'I Submit <3', 'freqList':[100], 'minLen':1, 'maxLen':1, 'default':['default']}

        #actual resources to be used

        self.resourceDict    = {'web':self.defaultWebList, 
                               'prompt':self.defaultPromptList,
                               'captions':self.defaultCaptionList,
                               'wallpapers':[],
                               'aud':[],
                               'img':[],
                               'vid':[],
                               'discord':'Playing with myself~'}

    def importPack(self, path) -> bool:
        try:
            print('starting import...')
            pack.name = path.split('\\').pop()
            #import all json file data
            for fileName in JSON_FILE_NAMES:
                print('importing', fileName)
                try:
                    fullPath = os.path.join(path, fileName + '.json')
                    with open(fullPath, 'r') as file:
                        self.resourceDict[fileName] = json.loads(file.read())
                except:
                    print('failed to import', fileName)

            print('importing wallpapers')
            for maybeWallpaper in os.listdir(path):
                try:
                    self.resourceDict['wallpapers'].append(os.path.join(path, maybeWallpaper)) if [maybeWallpaper.endswith(ext) for ext in WALL_FILE_TYPES].count(True) > 0 else ''#print('passed', maybeWallpaper)
                except Exception as e:
                    print(e)
                
            print('importing discord.dat')
            try:
                with open(os.path.join(path, 'discord.dat')) as file:
                    self.resourceDict['discord'] = file.readline().replace('\n', '')
            except:
                print('failed to import discord.dat')
            
            #resource path importing
            for media in MEDIA_TYPES:
                print('importing', media)
                try:
                    self.resourceDict[media] = [os.path.join(path, media, obj) for obj in os.listdir(os.path.join(path, media))]
                except:
                    print('failed to import', media, 'media')

            print('import done!')
            return True
        except Exception as e:
            print('error caught')
            print(e)
            return False

    #equivalent of save function
    def export(self, path, name) -> bool:
        try:
            print('starting export...')
            #build new path with pack name as its storage directory with subfolders (if not present)
            namedPath = os.path.join(path, name)
            if not os.path.exists(namedPath):
                print('created path')
                os.mkdir(namedPath)
            for media in MEDIA_TYPES:
                print('created /', media, '/', sep='')
                os.mkdir(os.path.join(namedPath, media)) if not os.path.exists(os.path.join(namedPath, media)) else ''
            
            #can be removed after next edgeware update probably
            print('applying caption fix')
            prefixSet = []
            for prefix in list(pack.resourceDict['captions'].keys()):
                prefixSet.append(prefixSet.append(prefix)) if not str(prefix) in ['default', 'prefix', 'subtext'] else ''
            try:
                while True:
                    prefixSet.remove(None)
            except:
                pass
            pack.resourceDict['captions']['prefix'] = prefixSet

            #saving json files
            print('saving json/text files')
            for fileName in JSON_FILE_NAMES:
                with open(os.path.join(namedPath, fileName + '.json'), 'w') as file:
                    file.write(json.dumps(self.resourceDict[fileName]))
            with open(os.path.join(namedPath, 'discord.dat'), 'w') as file:
                file.write(self.resourceDict['discord'])
            
            #copying audio/images/video from various sources into the final pack destination
            #   should not copy if already present
            print('aggregating wallpapers')
            for wallpaper in self.resourceDict['wallpapers']:
                dest = os.path.join(namedPath, wallpaper.split('\\').pop())
                if not os.path.exists(dest):
                    print('copying wallpaper', wallpaper)
                    shutil.copyfile(wallpaper, os.path.join(namedPath, wallpaper.split('\\').pop()))

            for media in MEDIA_TYPES:
                print('aggregating', media)
                for mediaFile in self.resourceDict[media]:
                    dest = os.path.join(namedPath, media, mediaFile.split('\\').pop())
                    if not os.path.exists(dest):
                        print('copying', mediaFile)
                        shutil.copyfile(mediaFile, dest)

            #cleaning pass to make sure no unsaved/unwanted files are present
            print('cleaning wallpapers')
            for file in os.listdir(namedPath):
                pp = [file==rName.split('\\').pop() for rName in self.resourceDict['wallpapers']]
                if pp.count(True) == 0 and file.split('\\').pop().split('.').pop() in WALL_FILE_TYPES:
                    os.remove(os.path.join(namedPath, file))


            for media in MEDIA_TYPES:
                print('cleaning', media)
                for file in os.listdir(os.path.join(namedPath, media)):
                    pp = [file==rName.split('\\').pop() for rName in self.resourceDict[media]]
                    if pp.count(True) == 0:
                        os.remove(os.path.join(namedPath, media, file))

            self.name = name
            print('save complete!')
            return True
        except Exception as e:
            print('caught error')
            print(e)
            return False

def showWindow() -> str:
    root = Tk()
    root.title('Edgeware Pack Editor')
    root.geometry('800x600')
    #root.iconbitmap(os.path.join(PATH, 'editor_assets', 'default_icon.ico'))

    menuBar = Menu(root)
    root.config(menu=menuBar)

    fileMenu = Menu(menuBar)
    fileMenu.add_command(label='New (Ctrl+N)', command=lambda:menuNew(True))
    def menuNew(isNew):
        global pack
        pack = Pack()
        resetList(audListBox, 'aud')
        resetList(imgListBox, 'img')
        resetList(vidListBox, 'vid')
        resetList(wPaperListBox, 'wallpapers')
        resetTree(promptTree, ['moods'])
        resetTree(captionTree, ['default'])
        resetTree(webTree, ['urls', 'args'])
        changeEntryText(subTextBox, 'I Submit <3')
        changeEntryText(subTextBox_Prompt, 'I Submit <3')
        packNameLabel.config(text='Unnamed Edgeware Pack')
        packDiscordLabel.config(text=pack.resourceDict['discord'])
        if isNew:
            fullAddTree_Prompts(promptTree)
            fullAddTree(captionTree)
    fileMenu.add_command(label='Open (Ctrl+O)', command=lambda:menuOpen('manual_select'))
    def menuOpen(openPath_):
        global pack, heldSavePath, hasBeenSaved
        if openPath_ == 'manual_select':
            openDir = filedialog.askdirectory(title='Open Pack Folder').replace('/', '\\')
        else:
            openDir = openPath_
        print(openDir)
        if not openDir == '' and not openDir == None:
            menuNew(False)
            hasBeenSaved = True
            heldSavePath = openDir
            pack = Pack()
            pack.importPack(openDir)
            #filling asset lists
            for path in pack.resourceDict['aud']:
                addList(audListBox, 'aud', True, path)
            for path in pack.resourceDict['img']:
                addList(imgListBox, 'img', True, path)
            for path in pack.resourceDict['vid']:
                addList(vidListBox, 'vid', True, path)
            for path in pack.resourceDict['wallpapers']:
                addList(wPaperListBox, 'wallpapers', True, path)
            #filling trees
            fullAddTree(captionTree)
            fullAddTree_Prompts(promptTree)
            fullAddTree_Web(webTree)

            #misc changes
            try:
                changeEntryText(subTextBox, pack.resourceDict['caption']['subtext'])
                changeEntryText(subTextBox_Prompt, pack.resourceDict['prompt']['subtext'])
            except:
                ''
            packNameLabel.config(text=pack.name)
            packDiscordLabel.config(text=pack.resourceDict['discord'])
            
    fileMenu.add_command(label='Save (Ctrl+S)', command=lambda:save())

    def save() -> bool:
        if not hasBeenSaved:
            return saveAs()
        return pack.export(heldSavePath, '')

    fileMenu.add_command(label='Save As (Ctrl+Shift+S)', command=lambda:saveAs())

    def saveAs() -> bool:
        global heldSavePath
        openDir = filedialog.askdirectory(title='Save Pack Folder As').replace('/', '\\')
        print(openDir)
        if not openDir == '' and not openDir == None:
            heldSavePath = openDir
            return pack.export(openDir, '')
        else:
            return False

    
    fileMenu.add_command(label='Import Zip', command=lambda:importZip())

    def importZip():
        zipPath = unpackZip()
        if zipPath != '':
            menuOpen(zipPath)


    fileMenu.add_command(label='Export Zip', command=lambda:exportZip())

    def exportZip():
        save()
        exportResource()

    fileMenu.add_command(label='Exit', command=lambda: os.kill(os.getpid(), 9))

    menuBar.add_cascade(label='File', menu=fileMenu)
    
    root.focus_set()
    root.bind('<Control-n>', lambda key: menuNew(False))
    root.bind('<Control-s>', lambda key: save())
    root.bind('<Control-Shift-S>', lambda key: saveAs())
    root.bind('<Control-o>', lambda key: menuOpen())

    tabMaster       = ttk.Notebook(root)
    tabGeneral      = ttk.Frame(None)
    tabMedia        = ttk.Frame(None)
    tabCaptions     = ttk.Frame(None)
    tabPrompts      = ttk.Frame(None)
    tabWeb          = ttk.Frame(None)

    #<======================================{GENERAL}======================================>
    tabMaster.add(tabGeneral, text='General')

    generalLeftFrame = Frame(tabGeneral, borderwidth=4, relief=RAISED)
    Label(generalLeftFrame, text='Pack Info').pack()
    packNameFrame = Frame(generalLeftFrame, borderwidth=2, relief=RAISED)
    packNameLabel = Label(packNameFrame, text=pack.name)
    #packRenameButton = Button(packNameFrame, text='Rename', command=lambda: renamePack())
    #def renamePack():
    #    newName = simpledialog.askstring('Rename', 'New Pack Name')
    #    if newName != '' and newName != None:
    #        pack.name = newName
    #        packNameLabel.config(text=newName)
    
    packDiscordFrame = Frame(generalLeftFrame, borderwidth=4, relief=RAISED)
    packDiscordLabel = Label(packDiscordFrame, text=pack.resourceDict['discord'])
    packUpdDiscButton = Button(packDiscordFrame, text='Edit', command=lambda: updateDisc())
    def updateDisc():
        newStat = simpledialog.askstring('Update', 'From: "' + pack.resourceDict['discord'] + '"\nNew:')
        if newStat != '' and newStat != None:
            pack.resourceDict['discord'] = newStat
            packDiscordLabel.config(text=newStat)

    generalRightFrame = Frame(tabGeneral, borderwidth=4, relief=RAISED)
    Label(generalRightFrame, text='Client Info').pack()
    
    versionInfoLabel = Label(generalRightFrame, text='Editor Version '+  LOCAL_VERSION)

    hotkeyInfo = '\tPrompt/Web Hotkeys\n\t\tDelete: deletes currently selected term\n\t\tC: Add a new category (category, mood, url)\n\t\tV: Add a new option to the selected category\n\t\tE: Edit the content of current selection\n\n\n\tMedia Hotkeys\n\t\tDelete: Deletes currently selected asset\n\t\tDouble Click/Enter: Previews the currently selected asset'

    hotkeyLabel = Label(generalRightFrame, foreground='darkgray', text=hotkeyInfo, relief='ridge')

    generalLeftFrame.pack(side='left', fill='both', expand=1)

    dummyFrame1 = Frame(generalLeftFrame)
    dummyFrame1.pack(fill='x')
    Label(dummyFrame1, text='Pack Name').pack(side='left')
    packNameFrame.pack(fill='x')
    packNameLabel.pack(side='top', fill='x', expand=1)
    #packRenameButton.pack(side='left', fill='x')

    dummyFrame2 = Frame(generalLeftFrame)
    dummyFrame2.pack(fill='x')
    Label(dummyFrame2, text='Discord Status').pack(side='left')
    packDiscordFrame.pack(fill='x')
    packDiscordLabel.pack(fill='x', side='left')
    packUpdDiscButton.pack(side='right', fill='x')

    generalRightFrame.pack(side='right', fill='both', expand=1)
    versionInfoLabel.pack()
    Label(generalRightFrame).pack()
    hotkeyLabel.pack(fill='x')

    #<===================================={END GENERAL}====================================>

    #<======================================={DRIVE}=======================================>
    tabMaster.add(tabMedia, text='Media')
    
    audFrame = Frame(tabMedia, borderwidth=4, relief=RAISED)
    Label(audFrame, text='Audio', borderwidth=2, relief=RAISED).pack(side='top', fill='x')
    audListBox = Listbox(audFrame)
    audListBox.bind('<Double-Button>', lambda key: os.startfile(pack.resourceDict['aud'][audListBox.curselection()[0]]))
    audListBox.bind('<Return>', lambda key: os.startfile(pack.resourceDict['aud'][audListBox.curselection()[0]]))
    audListBox.bind('<Delete>', lambda key: removeList(audListBox, 'aud'))

    imgFrame = Frame(tabMedia, borderwidth=4, relief=RAISED)
    Label(imgFrame, text='Images', borderwidth=2, relief=RAISED).pack(side='top', fill='x')
    imgListBox = Listbox(imgFrame)
    imgListBox.bind('<Double-Button>', lambda key: os.startfile(pack.resourceDict['img'][imgListBox.curselection()[0]]))
    imgListBox.bind('<Return>', lambda key: os.startfile(pack.resourceDict['img'][imgListBox.curselection()[0]]))
    imgListBox.bind('<Delete>', lambda key: removeList(imgListBox, 'img'))

    vidFrame = Frame(tabMedia, borderwidth=4, relief=RAISED)
    Label(vidFrame, text='Videos', borderwidth=2, relief=RAISED).pack(side='top', fill='x')
    vidListBox = Listbox(vidFrame)
    vidListBox.bind('<Double-Button>', lambda key: os.startfile(pack.resourceDict['vid'][vidListBox.curselection()[0]]))
    vidListBox.bind('<Return>', lambda key: os.startfile(pack.resourceDict['vid'][vidListBox.curselection()[0]]))
    vidListBox.bind('<Delete>', lambda key: removeList(vidListBox, 'vid'))

    wallpaperFrame = Frame(tabMedia, borderwidth=4, relief=RAISED)
    Label(wallpaperFrame, text='Wallpapers', borderwidth=2, relief=RAISED).pack(side='top', fill='x')
    wPaperListBox = Listbox(wallpaperFrame)
    wPaperListBox.bind('<Double-Button>', lambda key: os.startfile(pack.resourceDict['wallpapers'][wPaperListBox.curselection()[0]]))
    wPaperListBox.bind('<Return>', lambda key: os.startfile(pack.resourceDict['wallpapers'][wPaperListBox.curselection()[0]]))
    wPaperListBox.bind('<Delete>', lambda key: removeList(wPaperListBox, 'wallpapers'))

    #control buttons (aud => img => vid)
    addAudButton = Button(audFrame, text='Add...', 
        command=lambda: addList(audListBox, 'aud', False, None))
    removeAudButton = Button(audFrame, text='Remove Selected',
        command=lambda: removeList(audListBox, 'aud'))
    previewAudButton = Button(audFrame, text='Preview Selected',
        command=lambda: os.startfile(pack.resourceDict['aud'][audListBox.curselection()[0]]))
    resetAudButton = Button(audFrame, text='Remove All',
        command=lambda: resetList(audListBox, 'aud'))

    addImgButton = Button(imgFrame, text='Add...', 
        command=lambda: addList(imgListBox, 'img', False, None))
    removeImgButton = Button(imgFrame, text='Remove Selected',
        command=lambda: removeList(imgListBox, 'img'))
    previewImgButton = Button(imgFrame, text='Preview Selected',
        command=lambda: os.startfile(pack.resourceDict['img'][imgListBox.curselection()[0]]))
    resetImgButton = Button(imgFrame, text='Remove All',
        command=lambda: resetList(imgListBox, 'img'))

    addVidButton = Button(vidFrame, text='Add...', 
        command=lambda: addList(vidListBox, 'vid', False, None))
    removeVidButton = Button(vidFrame, text='Remove Selected',
        command=lambda: removeList(vidListBox, 'vid'))
    previewVidButton = Button(vidFrame, text='Preview Selected',
        command=lambda: os.startfile(pack.resourceDict['vid'][vidListBox.curselection()[0]]))
    resetVidButton = Button(vidFrame, text='Remove All',
        command=lambda: resetList(vidListBox, 'vid'))

    addWPaperButton = Button(wallpaperFrame, text='Add...', 
        command=lambda: addList(wPaperListBox, 'wallpapers', False, None))
    removeWPaperButton = Button(wallpaperFrame, text='Remove Selected',
        command=lambda: removeList(wPaperListBox, 'wallpapers'))
    previewWPaperButton = Button(wallpaperFrame, text='Preview Selected',
        command=lambda: os.startfile(pack.resourceDict['wallpapers'][wPaperListBox.curselection()[0]]))
    resetWPaperButton = Button(wallpaperFrame, text='Remove All',
        command=lambda: resetList(wPaperListBox, 'wallpapers'))

    audFrame.pack(side='left', fill='both', expand=1)
    audListBox.pack(side='top', fill='both', expand=1)
    addAudButton.pack(side='top', fill='x')
    removeAudButton.pack(side='top', fill='x')
    previewAudButton.pack(side='top', fill='x')
    Label(audFrame).pack(side='top')
    resetAudButton.pack(side='top', fill='x')

    imgFrame.pack(side='left', fill='both', expand=1)
    imgListBox.pack(side='top', fill='both', expand=1)
    addImgButton.pack(side='top', fill='x')
    removeImgButton.pack(side='top', fill='x')
    previewImgButton.pack(side='top', fill='x')
    Label(imgFrame).pack(side='top')
    resetImgButton.pack(side='top', fill='x')

    vidFrame.pack(side='left', fill='both', expand=1)
    vidListBox.pack(side='top', fill='both', expand=1)
    addVidButton.pack(side='top', fill='x')
    removeVidButton.pack(side='top', fill='x')
    previewVidButton.pack(side='top', fill='x')
    Label(vidFrame).pack(side='top')
    resetVidButton.pack(side='top', fill='x')

    wallpaperFrame.pack(side='right', fill='both', expand=1)
    wPaperListBox.pack(side='top', fill='both', expand=1)
    addWPaperButton.pack(side='top', fill='x')
    removeWPaperButton.pack(side='top', fill='x')
    previewWPaperButton.pack(side='top', fill='x')
    Label(wallpaperFrame).pack(side='top')
    resetWPaperButton.pack(side='top', fill='x')

    #<====================================={END DRIVE}=====================================>
    
    #<====================================={CAPTIONS}======================================>
    tabMaster.add(tabCaptions, text='Captions')

    captionTree = ttk.Treeview(tabCaptions)

    captionTree.focus_set()
    captionTree.bind('<Delete>', lambda key: removeTree(captionTree, captionTree.selection()[0], 'captions'))
    captionTree.bind('<c>', lambda key: addTree(captionTree, simpledialog.askstring('Category Name', 'Name of new category:'), True, 'captions'))
    captionTree.bind('<v>', lambda key: addTree(captionTree, simpledialog.askstring('Caption Text', 'Text for caption:'), False, 'captions'))
    captionTree.bind('<e>', lambda key: editTree(captionTree, captionTree.selection()[0], simpledialog.askstring('New Text', 'Updated caption:'), 'captions'))

    fullAddTree(captionTree)

    capOperatorPane = Frame(tabCaptions, borderwidth=4, relief=RAISED)
    Label(capOperatorPane, text='                ').pack(fill='x')
    addCapCategory = Button(capOperatorPane, text='Add Category', command=
        lambda: addTree(captionTree, simpledialog.askstring('Category Name', 'Name of new category:'), True, 'captions'))
    addCaption = Button(capOperatorPane, text='Add Caption', command=
        lambda: addTree(captionTree, simpledialog.askstring('Caption Text', 'Text for caption:'), False, 'captions'))
    editCaption = Button(capOperatorPane, text='Edit Caption', command=
        lambda: editTree(captionTree, captionTree.selection()[0], simpledialog.askstring('New Text', 'Updated caption:'), 'captions'))
    removeItem = Button(capOperatorPane, text='Delete Selected', command=
        lambda: removeTree(captionTree, captionTree.selection()[0], 'captions'))


    subTextBox = Entry(capOperatorPane)
    try:
        subTextBox.insert(0, pack.resourceDict['captions']['subtext'])
    except:
        subTextBox.insert(0, 'I submit <3')
        print('did not find subtext to load from caption.json')

    captionTree.pack(side='left', fill='both', expand=1)
    capOperatorPane.pack(side='right', fill='y')
    addCapCategory.pack(fill='x')
    addCaption.pack(fill='x')
    editCaption.pack(fill='x')
    removeItem.pack(fill='x')
    Label(capOperatorPane, text='                ').pack(fill='x')
    Label(capOperatorPane, text='Submission Button Text').pack(fill='x')
    subTextBox.pack(fill='x')
    Button(capOperatorPane, text='Update Subtext', command=lambda: assignSub(subTextBox.get())).pack()
    def assignSub(value):
        pack.resourceDict['captions']['subtext'] = value
    
    #<==================================={END CAPTIONS}====================================>
    
    #<====================================={PROMPTS}=======================================>
    tabMaster.add(tabPrompts, text='Prompts')

    promptTree = ttk.Treeview(tabPrompts)
    promptTree.focus_set()
    promptTree.bind('<Delete>', lambda key: removeTree(promptTree, promptTree.selection()[0], 'prompt'))
    promptTree.bind('<c>', lambda key: addTree(promptTree, simpledialog.askstring('Mood Name', 'Name of new mood:'), True, 'prompt'))
    promptTree.bind('<v>', lambda key: addTree(promptTree, simpledialog.askstring('Asset Text', 'Text for asset:'), False, 'prompt'))
    promptTree.bind('<e>', lambda key: editTree(promptTree, promptTree.selection()[0], simpledialog.askstring('New Text', 'Updated asset:'), 'prompt'))

    fullAddTree_Prompts(promptTree)

    promptOperatorPane = Frame(tabPrompts, borderwidth=4, relief=RAISED)
    Label(promptOperatorPane, text='                ').pack(fill='x')
    addPromptCategory = Button(promptOperatorPane, text='Add Mood', command=
        lambda: addTree(promptTree, simpledialog.askstring('Mood Name', 'Name of new mood:'), True, 'prompt'))
    addPrompt = Button(promptOperatorPane, text='Add Option', command=
        lambda: addTree(promptTree, simpledialog.askstring('Asset Text', 'Text for asset:'), False, 'prompt'))
    editPrompt = Button(promptOperatorPane, text='Edit Prompt', command=
        lambda: editTree(promptTree, promptTree.selection()[0], simpledialog.askstring('New Text', 'Updated asset:'), 'prompt'))
    removePrompt = Button(promptOperatorPane, text='Delete Selected', command=
        lambda: removeTree(promptTree, promptTree.selection()[0], 'prompt'))

    subTextBox_Prompt = Entry(promptOperatorPane)
    try:
        subTextBox_Prompt.insert(0, pack.resourceDict['prompt']['subtext'])
    except:
        subTextBox_Prompt.insert(0, 'I submit <3')
        print('did not find subtext to load from prompt.json')

    minLenSpinner = Spinbox(promptOperatorPane, from_=1, to=100)
    minLenSpinner.insert(0, pack.resourceDict['prompt']['minLen'])
    maxLenSpinner = Spinbox(promptOperatorPane, from_=1, to=101)
    maxLenSpinner.insert(0, pack.resourceDict['prompt']['maxLen'])

    promptTree.pack(side='left', fill='both', expand=1)
    promptOperatorPane.pack(side='right', fill='y')
    addPromptCategory.pack(fill='x')
    addPrompt.pack(fill='x')
    editPrompt.pack(fill='x')
    removePrompt.pack(fill='x')
    Label(promptOperatorPane, text='                ').pack(fill='x')
    Label(promptOperatorPane, text='Submission Button Text').pack(fill='x')
    subTextBox_Prompt.pack(fill='x')
    Button(promptOperatorPane, text='Update Subtext', command=lambda: assignSub_P(subTextBox_Prompt.get())).pack()
    def assignSub_P(value):
        pack.resourceDict['prompt']['subtext'] = value
    Label(promptOperatorPane, text='minLen').pack(fill='x')
    minLenSpinner.pack(fill='x')
    Label(promptOperatorPane, text='maxLen').pack(fill='x')
    maxLenSpinner.pack(fill='x')
    Button(promptOperatorPane, text='Update Lengths', command=lambda: assignLens()).pack(fill='x')
    def assignLens():
        if int(maxLenSpinner.get()) < int(minLenSpinner.get()):
            messagebox.showerror('Error', 'Could not set lengths.\nMin must be less than max.')
            return False
            
        pack.resourceDict['prompt']['minLen'] = minLenSpinner.get()
        pack.resourceDict['prompt']['maxLen'] = maxLenSpinner.get()
        print(pack.resourceDict['prompt'])
        

    #<==================================={END PROMPTS}=====================================>
    
    
    #<======================================={WEB}=========================================>
    tabMaster.add(tabWeb, text='Web')

    webTree = ttk.Treeview(tabWeb)

    webTree.focus_set()
    webTree.bind('<Delete>', lambda key: removeWeb())
    webTree.bind('<c>', lambda key: addWeb(simpledialog.askstring('URL Arg', 'Base of link to use:'), True))
    webTree.bind('<v>', lambda key: addWeb(simpledialog.askstring('URL Arg', 'Base of link to use:'), True))
    webTree.bind('<e>', lambda key: editWeb(simpledialog.askstring('New Text', 'Updated arg:')))

    #good god why did i do the web.json like i did it's so fucking bad
    fullAddTree_Web(webTree)

    webOperatorPane = Frame(tabWeb, borderwidth=4, relief=RAISED)
    Label(webOperatorPane, text='                ').pack(fill='x')
    addLink = Button(webOperatorPane, text='Add URL', command=
        lambda: addWeb(simpledialog.askstring('URL Arg', 'Base of link to use:'), True))
    addArg = Button(webOperatorPane, text='Add Arg', command=
        lambda: addWeb(simpledialog.askstring('URL Arg', 'Text for caption:'), False))
    editArg = Button(webOperatorPane, text='Edit Arg', command=
        lambda: editWeb(simpledialog.askstring('New Text', 'Updated arg:')))
    removeItem_Web = Button(webOperatorPane, text='Delete Selected', command=
        lambda: removeWeb())
    
    def addWeb(text, urlMode):
        if urlMode:
            webTree.insert('urls', 'end', text, text=text)
            pack.resourceDict['web']['urls'].append(text)
            pack.resourceDict['web']['args'].append('')
        else:
            expectedParent=webTree.selection()[0]
            if expectedParent == 'urls':
                return False
            while webTree.parent(expectedParent) != 'urls':
                expectedParent = webTree.parent(expectedParent)
            webTree.insert(expectedParent, 'end', text=text)
            pack.resourceDict['web']['args'][pack.resourceDict['web']['urls'].index(expectedParent)] += ',' + text
        print(pack.resourceDict['web']['urls'])
        print(pack.resourceDict['web']['args'])

    def editWeb(arg):
        parent = webTree.parent(webTree.selection()[0])
        if parent == '' or parent == 'urls':
            return False
        webTree.insert(parent, 'end', text=arg)

        pack.resourceDict['web']['args'][pack.resourceDict['web']['urls'].index(parent)] = pack.resourceDict['web']['args'][pack.resourceDict['web']['urls'].index(parent)].replace(webTree.selection()[0], '')
        pack.resourceDict['web']['args'][pack.resourceDict['web']['urls'].index(parent)] += ',' + arg

        webTree.delete(webTree.selection()[0])

    def removeWeb():
        parent = webTree.parent(webTree.selection()[0])
        if parent == '':
            return False
        if parent == 'urls':
            selectedIndex = pack.resourceDict['web']['urls'].index(webTree.selection()[0])
            pack.resourceDict['web']['args'].pop(selectedIndex)
            pack.resourceDict['web']['urls'].pop(selectedIndex)
        else:
            print(pack.resourceDict['web']['urls'].index(webTree.parent(webTree.selection()[0])))
            pack.resourceDict['web']['args'][pack.resourceDict['web']['urls'].index(webTree.parent(webTree.selection()[0]))] = (
                pack.resourceDict['web']['args'][pack.resourceDict['web']['urls'].index(webTree.parent(webTree.selection()[0]))].replace(
                    webTree.item(webTree.selection()[0])['text'], ''
                )
            )
        webTree.delete(webTree.selection()[0])

    webTree.pack(side='left', fill='both', expand=1)
    webOperatorPane.pack(side='right', fill='y')
    addLink.pack(fill='x')
    addArg.pack(fill='x')
    editArg.pack(fill='x')
    removeItem_Web.pack(fill='x')
    Label(webOperatorPane, text='                ').pack(fill='x')
    
    #<====================================={END WEB}=======================================>

    tabMaster.pack(expand=1, fill='both')

    root.mainloop()

def changeEntryText(tkEntryObj, nText):
    tkEntryObj.delete(0, 99999)
    tkEntryObj.insert(0, nText)

def fullAddTree(tkTreeObj):
    try:
        tkTreeObj.insert('', 0, 'default', text='default')
    except:
        'just ignore it lmao i know how stupid i am'
    for caption in pack.resourceDict['captions']['default']:
        tkTreeObj.insert('default', 'end', caption, text=caption)
    for prefix in list(pack.resourceDict['captions'].keys()):
        if prefix == 'default' or prefix == 'subtext':
            continue
        tkTreeObj.insert('', 'end', prefix, text=prefix)
        for caption in pack.resourceDict['captions'][prefix]:
            tkTreeObj.insert(prefix, 'end', text=caption)
            
def fullAddTree_Web(tkTreeObj):
    try:
        tkTreeObj.insert('', 0, 'urls', text='urls')
    except:
        'just ignore it lmao i know how stupid i am'
    for url in pack.resourceDict['web']['urls']:
        tkTreeObj.insert('urls', 'end', url, text=url)
        for arg in pack.resourceDict['web']['args'][pack.resourceDict['web']['urls'].index(url)].split(','):
            if arg == '':
                continue
            tkTreeObj.insert(url, 'end', text=arg)

def fullAddTree_Prompts(tkTreeObj):
    try:
        tkTreeObj.insert('', 0, 'moods', text='moods')
    except:
        'just ignore it lmao i know how stupid i STILL am'
    for caption in pack.resourceDict['prompt']['moods']:
        tkTreeObj.insert('moods', 'end', caption, text=caption)
    for mood in pack.resourceDict['prompt']['moods']:
        try:
            parent = tkTreeObj.insert('', 'end', text=mood)
            for option in pack.resourceDict['prompt'][mood]:
                tkTreeObj.insert(parent, 'end', text=option)
        except Exception as e:
            print(e)

def addTree(tkTreeObj, key, rootMode, dictKey):
    if rootMode:
        if list(pack.resourceDict[dictKey].keys()).count(key) == 0:
            tkTreeObj.insert('', 'end', text=key)
            pack.resourceDict[dictKey][key] = []
            if dictKey == 'prompt':
                pack.resourceDict['prompt']['freqList'].append(50)
    else:
        expectedParent=tkTreeObj.selection()[0]
        while tkTreeObj.parent(expectedParent) != '':
            expectedParent = tkTreeObj.parent(expectedParent)
        tkTreeObj.insert(expectedParent, 'end', text=key)
        pack.resourceDict[dictKey][tkTreeObj.item(expectedParent)['text']].append(key)

def editTree(tkTreeObj, key, value, dictKey):
    if tkTreeObj.parent(key) == '' or value == '':
        return False
    parent = tkTreeObj.parent(key)
    pack.resourceDict[dictKey][parent].remove(key)
    pack.resourceDict[dictKey][parent].append(value)

    tkTreeObj.delete(key)
    tkTreeObj.insert(parent, 'end', text=value)

def removeTree(tkTreeObj, key, dictKey):
    if (key == 'default' and dictKey == 'captions') or (key == 'moods' and dictKey == 'prompt'):
        return False
    #determine if category vs caption was deleted
    if tkTreeObj.parent(key) == '':
        if dictKey == 'prompt':
            try:
                pack.resourceDict['prompt']['freqList'].pop(pack.resourceDict['prompt']['moods'].index(tkTreeObj.item(key)['text']))
            except:
                tkTreeObj.delete(key)
        pack.resourceDict[dictKey].pop(tkTreeObj.item(key)['text'])
    else:
        pack.resourceDict[dictKey][tkTreeObj.item(tkTreeObj.parent(key))['text']].remove(tkTreeObj.item(key)['text'])
        if tkTreeObj.parent(key) == 'moods' or tkTreeObj.parent(key) == 'prompt':
            try:
                for entry in tkTreeObj.get_children():
                    if tkTreeObj.item(entry)['text'] == key:
                        tkTreeObj.delete(entry)
            except:
                ''
    tkTreeObj.delete(key)

def resetTree(tkTreeObj, ignoreList):
    for child in tkTreeObj.get_children():
        if not child in ignoreList:
            tkTreeObj.delete(child)
        else:
            for grandchild in tkTreeObj.get_children(child):
                tkTreeObj.delete(grandchild)

def addList(tkListObj, key, autoState, optPath):
    if not autoState:
        path_ = filedialog.askopenfilenames(title='Select ' + key + ' file(s)')
        if(len(path_) > 0 and path_ != None):
            for path in path_:
                print(path)
                pack.resourceDict[key].append(path)
                tkListObj.insert(tkListObj.size(), path.split('/').pop())
    else:
        tkListObj.insert(pack.resourceDict[key].index(optPath), optPath.split('\\').pop())

def removeList(tkListObj, key):
    index = int(tkListObj.curselection()[0])
    try:
        pack.resourceDict[key].pop(index)
        tkListObj.delete(index)
    except Exception as e:
        print('could not remove item from list;', e)

def resetList(tkListObj, key):
    try:
        tkListObj.delete(0, tkListObj.size())
        pack.resourceDict[key] = []
    except Exception as e:
        print('could not reset list')
        print(e)

#taken and slightly modified from config
#:) i am very creative yes
def exportResource():
    try:
        saveLocation = filedialog.asksaveasfile('w', title='Save Zip Location', defaultextension ='zip')
        print('starting save to', saveLocation)
        with zipfile.ZipFile(saveLocation.name.replace('/', '\\'), 'w', compression=zipfile.ZIP_DEFLATED) as zip:
            beyondRoot = False
            for root, dirs, files in os.walk(heldSavePath.replace('/', '\\')):
                for obj in files:
                    if obj.endswith('.zip'):
                        print('skipped packing zip file')
                        continue
                    print('packing', os.path.join(root, obj))
                    if beyondRoot:
                        zip.write(os.path.join(root, obj), root.split('\\')[len(root.split('\\')) - 1] + '\\' + obj)
                    else:
                        zip.write(os.path.join(root, obj), '\\' + obj)
                for dir in dirs:
                    zip.write(os.path.join(root, dir), '\\' + dir + '\\')
                beyondRoot = True
        print('zip file write completed')
    except:
        messagebox.showerror('Write Error', 'Failed to export resource to zip file.')

def unpackZip() -> str:
    try:
        zipPath = filedialog.askopenfile('r', title='Unpack Zip', defaultextension ='zip').name.replace('/', '\\')
        print('attempted to unpack', zipPath, '\n\tthis may take some time...')
        with zipfile.ZipFile(zipPath, 'r') as obj:
            obj.extractall(os.path.join(PATH, zipPath.split('\\').pop().split('.')[0]))
        print('unpacking done')
        return os.path.join(PATH, zipPath.split('\\').pop().split('.')[0])
    except:
        print('failed to unpack zip')
        return ''

pack = Pack()
showWindow()