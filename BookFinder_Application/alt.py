from tkinter import *
from PIL import Image, ImageTk
from tkinter import messagebox, filedialog
import os, pandas
from Ext_modules import requests_with_caching


request_with_caching = requests_with_caching()





class BookFinder:
    def __init__(self):
        global Title_var
        global Author_var
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

        SearchButton = Button(container, text = "Search", font = ("Tahoma", "10", "bold"), fg = "#021214", bg = "Azure", command = self.getBook)
        SearchButton.place(x=55, y = 115)

        UploadBtn = Button(container, text = "Upload File", font = ("Tahoma", "10", "bold"), fg = "#021214", bg = "Azure", command = self.getBook_from_file)
        UploadBtn.place(x = 200, y = 115)

        def responsive():
            win = window.winfo_width()
            x = (38/100)*win
            container.configure(width = x)
            # container.place(x = 10, y = 20)
            window.after(100,responsive)
        responsive()
        window.mainloop()

    def getBook(self):
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
            result = "text"
            # result = result = request_with_caching.get(base_url = "https://www.googleapis.com/books/v1/volumes", params_d = d)
            result_dict = {f'Title = {bookTitle} and Author = {bookAuthor}':result}
            error = "None"
            self.displayResult(result_dict, error)


    def getBook_from_file(self):
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
            self.displayResult(result_dict, error)


    def displayResult(self, result, error):
        if error == "no column":
            messagebox.showinfo("Alert", '''No Result Found!
    The uploaded file is either empty or does not contain a column(s) named "title" and/or "author".

    POSSIBLE FIX: Make sure the uploaded file is not empty and title the title and author columns(if present) as "title" and "author" respectively. ''')

        elif error == "empty columns":
            messagebox.showinfo("Alert", '''No Result Found!
    The "title" and/or "author" columns of the uploaded file does not contain any data.

    POSSIBLE FIX: Make sure that atleast one of the above named columns of the uploaded file is not empty. ''')
        else:
            displayPanel = Toplevel()
            displayPanel.wm_title(f'Search Results for {"".join([key for key in result.keys()])}')
            displayPanel.geometry('500x500')
            displayPanel.minsize(500, int(displayPanel.maxsize()[1]))
            displayPanel.resizable(1,1)
            displayPanel.state('zoomed')

            w = int((displayPanel.maxsize()[0])/3)



            search_lab = Label(displayPanel, width =w , bg = "red", text = "SEARCHED BOOKS", font =("Tahoma", "12", "bold"), fg = "white")
            search_lab.place(x=0, y=0)


            searchresult_lab = Label(displayPanel, height = 5, width =w,  bg = "brown", text = "SEARCH RESULT", font =("Tahoma", "12", "bold"), fg = "white" )
            searchresult_lab.place(x=w, y=0)


            selected_result_lab = Label(displayPanel, height = 5, width =w, bg = "yellow", text = "SELECTED BOOKS", font =("Tahoma", "12", "bold"), fg = "white" )
            selected_result_lab.place(x=2*w, y=0)
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




BookFinder = BookFinder()
