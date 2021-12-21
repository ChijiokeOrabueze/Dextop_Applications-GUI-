from tkinter import *
from PIL import Image, ImageTk
from tkinter import messagebox, filedialog
import os, pandas,json
from Ext_modules import requests_with_caching
from openpyxl import load_workbook


request_with_caching = requests_with_caching()

def saveBook(book_to_add):
    df = pandas.DataFrame(book_to_add)
    writer = pandas.ExcelWriter("Book.xlsx", engine = 'openpyxl')
    writer.book = load_workbook("Book.xlsx")
    writer.sheets = dict((ws.title, ws) for ws in writer.book.worksheets)
    reader = pandas.read_excel(r'Book.xlsx')
    df.to_excel(writer, index = False, header = False, startrow = len(reader)+1)
    writer.close()



def getInfo(family, btn):
    x=0
    output_dic = {}
    lst_keys = ["Title", "Subtitle", "Author", "Publisher", "Place", "Date", "Page", "Category", "ISBN", "ibgn"]
    lst_keys_INDEX = 0
    for obj in family:
        if x%2 == 0:
            pass
        elif x == len(family) - 4:
            if obj.get().strip() == "":
                pass
            else:
                output_dic[lst_keys[lst_keys_INDEX]] = [obj.get().strip()]
                break
        elif x == len(family) -2:
            output_dic[lst_keys[lst_keys_INDEX]] = [obj.get().strip()]
        else:
            output_dic[lst_keys[lst_keys_INDEX]] = [obj.get().strip()]
            lst_keys_INDEX+=1
        x+=1
    saveBook(output_dic)


def getBook():
    bookTitle = Title_var.get().strip()
    bookAuthor = Author_var.get().strip()

    if bookTitle == "" and bookAuthor == "":
        Titleinfo.configure(text = "Please enter a book title and/or an author name below or use the 'upload file' button.")
    else:
        if bookTitle != "" and bookAuthor == "":
            d = {"q":f'{bookTitle}+intitle:{bookTitle}'}
        elif bookAuthor != "" and bookTitle == "":
            d = {"q":f'{bookAuthor}+inauthor:{bookAuthor}'}
        else:
            d = {"q":f'{bookTitle}+intitle:{bookTitle}+inauthor:{bookAuthor}'}
        result = request_with_caching.get(base_url = "https://www.googleapis.com/books/v1/volumes", params_d = d)
        result_dict = {f'Title = {bookTitle} and Author = {bookAuthor}':result}
        error = "None"
        displayResult(result_dict, error)




def getBook_from_file():
    file = filedialog.askopenfilename(title = 'open')
    allowedFiles = ['.csv', '.txt', '.xlsx']
    filename = file.split('/')[-1]
    _, file_ext = os.path.splitext(filename)
    if file_ext not in allowedFiles and file != "":
        messagebox.showinfo('Alert', "File type not allowed. Please upload an Excel, Text or csv file.")

    else:
        result_dict = {}
        if file_ext == allowedFiles[-1]:
            df = pandas.read_excel(file)
        else: df = pandas.read_csv(file)
        Titledata = pandas.DataFrame({'Title':[]})
        Authordata = pandas.DataFrame({'Author':[]})
        lower_case_columns = [x.lower() for x in df.columns]
        if "title" in lower_case_columns and "author" in lower_case_columns:
            print("title and author")
            for column in df.columns:
                if column.lower() == "title":
                    Titledata = df[column]
                elif column.lower() == "author":
                    Authordata = df[column]

        elif "title" in lower_case_columns:
            print("title")
            for column in df.columns:
                if column.lower() == "title":
                    Titledata = df[column]
                    Authordata['Author'] = len(Titledata.index)*[" "]
                    Authordata = Authordata['Author']

        elif "author" in lower_case_columns:
            print("author")
            for column in df.columns:
                if column.lower() == "author":
                    Authordata = df[column]
                    Titledata['Title'] = len(Authordata.index)*[" "]
                    Titledata = Titledata['Title']

        else:
            print("no column named author and or title")
            Authordata = Authordata['Author']
            Titledata = Titledata['Title']
            error = "no column"

        temp_params_d_lst = []
        search_lst = []
        for title, author in zip(Titledata, Authordata):
            title = str(title).strip()
            author = str(author).strip()
            print(title,author)
            if title == "Nan":
                title = ""
            if author == "Nan":
                author = ""
            search_lst.append(f'Title={title} and Author{author}')
            if title != "" and author != "":
                d = {"q":f'{title}+intitle:{title}+inauthor:{author}'}
                temp_params_d_lst.append(d)
            elif title != "":
                d = {"q":f'{title}+intitle:{title}'}
                temp_params_d_lst.append(d)
            elif author != "":
                d = {"q":f'{author}+inauthor:{author}'}
                temp_params_d_lst.append(d)
            else:
                d = {"q":f'{title}+intitle:{title}+inauthor:{author}'}
                temp_params_d_lst.append(d)
                print("No result found. Please ensure the file uploaded is not an empty file and") #it contains a column named title and/or author")
            error = "empty columns"

        for param_d, item in zip(temp_params_d_lst,search_lst):
            if param_d["q"][0] == "+" and param_d["q"][9] == "+":
                result_dict[item] = '{}'
            else:
                result = request_with_caching.get(base_url = "https://www.googleapis.com/books/v1/volumes", params_d = param_d)
                result_dict[item] = result
                error = None
        displayResult(result_dict, error)


def displayResult(result, error):
    if error == "no column":
        messagebox.showinfo("Alert", '''No Result Found!
The uploaded file is either empty or does not contain a column(s) named "title" and/or "author".

POSSIBLE FIX: Make sure the uploaded file is not empty and title the title and author columns(if present) as "title" and "author" respectively. ''')

    elif error == "empty columns":
        messagebox.showinfo("Alert", '''No Result Found!
The "title" and/or "author" columns of the uploaded file does not contain any data.

POSSIBLE FIX: Make sure that atleast one of the above named columns of the uploaded file is not empty. ''')
    else:
        def get_selected(event, index = None):
            # try:
            if index is None:
                index = searched_items.curselection()
            selected_item = searched_items.get(index)
            inWord = False
            words= []
            for word in selected_item:
                if inWord:
                    words.append(word)
                elif word == " ":
                    inWord = True

            selected_item = "".join(words)
            output_items = result[selected_item]
            # print(output_items)
            book = json.loads(output_items)

            def createInput(parent, label_name, input_value, x, y):
                label = Label(parent, text = label_name, bg = "#f4f4f4", height = 1, font = ("Times", "10", "bold"))
                label.place(x=x, y = y)
                ent_var = StringVar()
                entry = Entry(parent, textvariable = ent_var, font = ("Times", "12"), width = 43)
                entry.place(x = x+75, y = y)
                entry.insert(END,input_value)





            def checkget(key,value):
                try:
                    return key[value]
                except:
                    return "None"

            if book == {}:
                pass
            else:
                div = scrollable_frame.winfo_children()
                if len(div) == 0:
                    pass
                else:
                    for obj in div:
                        obj.destroy()
                totalItem = book['totalItems']
                print(totalItem)
                x =0
                startx = 0
                starty = 0
                for item in book['items']:
                    if x%2 == 0:
                        books_div = Frame(scrollable_frame, bg = "white", height = 380, width = 900)
                        # book_div.place(x=startx, y =starty )
                        books_div.pack(padx=10, pady=10)
                        startx = 0
                        starty = 0
                    else:
                        pass
                    book_div = Frame(books_div, height = 380, width = 427, bg = "#f4f4f4")
                    book_div.place(x=startx, y =starty )
                    # book_div.pack(padx=10, pady=10)


                    bookInfo=item['volumeInfo']
                    bookInfo1 =bookInfo['industryIdentifiers']
                #     print(bookInfo)
                    createInput(book_div, "Title", checkget(bookInfo,'title'), 0, 0)
                    createInput(book_div, "Subtitle",checkget(bookInfo,'subtitle'), 0, 35)
                    createInput(book_div, "Author" , checkget(bookInfo, 'authors'), 0, 70)
                    createInput(book_div, "publisher" , checkget(bookInfo, 'publisher'), 0, 105)
                    createInput(book_div, "place" , checkget(bookInfo,'publisher'), 0, 140)
                    createInput(book_div, "publish_date" , checkget(bookInfo, 'publishedDate')[:4], 0, 175)
                    createInput(book_div, "page" , checkget(bookInfo, 'pageCount'), 0, 210)
                    createInput(book_div, "categories" , checkget(bookInfo, 'categories'), 0, 245)
                    y = 275
                    for info in bookInfo1:
                        createInput(book_div, info['type'] , checkget(info, 'identifier'), 0, y)
                        y+=35
                    button = Button(book_div, text = "select to save")
                    button.config(command= lambda family = book_div.winfo_children(), btn = button: getInfo(family,btn))
                    button.place(x=75, y = y+10 )
                    startx += 439
                    x+=1
                    # print(book_div.winfo_children()[1].get())
                    # print("______________________")
                    # print(book_div.place_slaves())

                print(x)
            # except:
            #     pass




        displayPanel = Toplevel()
        if len(result) == 1:
            displayPanel.wm_title(f'Search Results for {"".join([key for key in result.keys()])}')
        else:
            displayPanel.wm_title('Multiple Search Results for file upload')
        displayPanel.geometry('500x500')
        displayPanel.minsize(500, int(displayPanel.maxsize()[1]))
        displayPanel.resizable(1,1)
        displayPanel.state('zoomed')

        w = int((window.maxsize()[0])/3)


        search_lab = Label(displayPanel , bg = "Azure",height= 4, text = "SEARCHED BOOKS", font =("Tahoma", "12", "bold"), fg = "Tomato", justify="left", width = 46, padx = 0)
        search_lab.place(x=0, y=0)
        holder1 = Frame(displayPanel, bg = "Azure", width = 455, height = 633)
        holder1.place(x = 0, y = 70)
        searched_items = Listbox(holder1, bg = "Azure", fg = "Tomato", width = 73, height = 41)
        searched_items.place(x=0, y = 0)
        Sb1 = Scrollbar(holder1, bg = "Azure", width = 20 )
        Sb1.place(x= 430, y = 20)
        searched_items.configure(yscrollcommand=Sb1.set)
        Sb1.configure(command=searched_items.yview)
        searched_items.bind('<<ListboxSelect>>', get_selected)


        searchresult_lab = Label(displayPanel, width =92, height= 4,  bg = "Azure", text = "SEARCH RESULT", font =("Tahoma", "12", "bold"), fg = "Green" )
        searchresult_lab.place(x=w, y=0)
        holder2 = Frame(displayPanel, bg = "White", width = 910, height = 633)
        holder2.place(x = w, y = 70)
        output_results = Canvas(holder2,width = 885, height = 633, bg = "White")#,
        output_results.pack(side = "left", fill = "both", expand = True)
        # output_results.place(x=0, y = 0)
        scrollable_frame = Frame(output_results, bg = "white")
        scrollable_frame.bind("<Configure>", lambda e: output_results.configure(scrollregion = output_results.bbox('all')))
        output_results.create_window((1,1),window = scrollable_frame, anchor = "nw")
        Sb2 = Scrollbar(holder2, bg = "Azure", width = 20 )
        Sb2.pack(side = "left", fill = "y")
        # Sb2.place(x= 860, y = 20)
        output_results.configure(yscrollcommand=Sb2.set)
        Sb2.configure(command=output_results.yview)



        # selected_result_lab = Label(displayPanel, width =46,height= 4, bg = "Azure", text = "SELECTED BOOKS", font =("Tahoma", "12", "bold"), fg = "Green" )
        # selected_result_lab.place(x=2*w, y=0)
        # holder3 = Frame(displayPanel, bg = "Azure", width = 455, height = 633)
        # holder3.place(x = 2*w, y = 70)
        # selected_results = Canvas(holder3, width = 435, height = 633, bg = "Azure")
        # selected_results.place(x=0, y = 0)
        # Sb3 = Scrollbar(holder3, bg = "Azure", width = 20 )
        # Sb3.place(x= 430, y = 20)
        # selected_results.configure(yscrollcommand=Sb3.set)
        # Sb3.configure(command=selected_results.yview)

        #populating the serach displayPanel
        index = 1
        for key in result.keys():
            searched_items.insert(END,str(index) + ". " +key)
            index+=1
        get_selected(event= '<<ListboxSelect>>',index=0)






        # displayPanel.configure(bg = "black")
        #
        # w = displayPanel.maxsize()[0]
        # h = displayPanel.maxsize()[1]
        #
        # bg_im = Image.open("image.jpg")
        # # bg_im = bg_im.resize((w,h), Image.ANTIALIAS)
        # pho = ImageTk.PhotoImage(bg_im)
        # lab = Label(displayPanel)
        # lab.configure(image = pho)
        # lab.place(x=0, y = 0)









window = Tk()
window.wm_title('BookFinder')
window.geometry('500x500')
window.minsize(500, int(window.maxsize()[1]))
window.resizable(1,1)
window.state('zoomed')
window.configure(bg = "black")

w = window.maxsize()[0]
h = window.maxsize()[1]
# print(window.winfo_screenwidth())
# print(h)







file = Image.open("image.jpg")
file = file.resize((w,h), Image.ANTIALIAS)
photo = ImageTk.PhotoImage(file)
fill = Label(window, image = photo)
fill.place(x=0, y = 0, relwidth = 1, relheight = 1)

container = Frame(window, bg = "#021214", height = 200, width = 520)
container.place(x=430, y = 200)

# print(container.winfo_reqwidth())



Title_var = StringVar()
TitleLabel = Label(container, text = "Title", bg = "#021214", fg="white", height = 1, font = ("Times", "10", "bold"))
TitleLabel.place(x =10, y = 20 )
TitleField = Entry(container, textvariable = Title_var, width = 50, font = ("Times", "14"))
TitleField.place(x = 55, y =20)
Titleinfo = Label(container, text = "", fg = "red", bg = "#021214", pady = 0)
Titleinfo.place(x = 55, y = 45)

Author_var = StringVar()
AuthorLabel = Label(container, text = "Author", bg = "#021214", fg="white", height = 1, font = ("Times", "10", "bold"))
AuthorLabel.place(x =10, y = 65 )
AuthorField = Entry(container, textvariable = Author_var, width = 50, font = ("Times", "14"))
AuthorField.place(x = 55, y =65)
Authorinfo = Label(container, text = "", bg = "#021214", fg = "red", pady = 0)
Authorinfo.place(x = 55, y = 90)

SearchButton = Button(container, text = "Search", font = ("Tahoma", "10", "bold"), fg = "#021214", bg = "Azure", command = getBook)
SearchButton.place(x=55, y = 115)

UploadBtn = Button(container, text = "Upload File", font = ("Tahoma", "10", "bold"), fg = "#021214", bg = "Azure", command = getBook_from_file)
UploadBtn.place(x = 200, y = 115)

def responsive():
    win = window.winfo_width()
    x = (38/100)*win
    container.configure(width = x)
    # container.place(x = 10, y = 20)
    window.after(100,responsive)
responsive()
window.mainloop()
