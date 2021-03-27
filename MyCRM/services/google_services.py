clientID='755545689580-ku1hogmosj7ml4f4n66ar5shn7ujajbj.apps.googleusercontent.com'
clientSecret='_YKX-eyhKUktRn6BfzYgpxVO'

# from __future__ import print_function
import pickle
import os.path
from abc import ABC, abstractmethod
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.


class Import_from_google_sheets(ABC):
    SAMPLE_SPREADSHEET_ID = None
    SAMPLE_RANGE_NAME = None

    @classmethod
    def __get_data__(cls):
        """Shows basic usage of the Sheets API.
        Prints values from a sample spreadsheet.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=cls.SAMPLE_SPREADSHEET_ID,
                                    range=cls.SAMPLE_RANGE_NAME).execute()
        return result.get('values', [])

    @abstractmethod
    def handled_data(cls):
        pass


class importTradeChas(Import_from_google_sheets):
    SAMPLE_SPREADSHEET_ID = '16Nkq7PLHNfif6mZEZDOoNkB68jjyOR-3Ca_rlM7OxAI'
    SAMPLE_RANGE_NAME = 'трейдчасЭкспорт!D2:F1000'

    @classmethod
    def handled_data(cls):
        # TradeChasStock.objects.all().delete()
        values=cls.__get_data__()
        values=list(filter(lambda x:(x[1]!='' and x[2]!='0'), values)) # удаляем строки с пробелами
        return values
        # values = map(lambda x: TradeChasStock(item=x[0], count=x[1]), values)
        # TradeChasStock.objects.bulk_create(values)



class importMyStockVostok(Import_from_google_sheets):
    SAMPLE_SPREADSHEET_ID = '16Nkq7PLHNfif6mZEZDOoNkB68jjyOR-3Ca_rlM7OxAI'
    SAMPLE_RANGE_NAME = 'МоиВосток!H2:L1000'

    @classmethod
    def handled_data(cls):
            values = cls.__get_data__()
            values = list(filter(lambda x: (x[0] != '') and int(x[2])>0, values))  # удаляем строки с пробелами
            return values

class importMyStockMoskvin(Import_from_google_sheets):
    SAMPLE_SPREADSHEET_ID = '16Nkq7PLHNfif6mZEZDOoNkB68jjyOR-3Ca_rlM7OxAI'
    SAMPLE_RANGE_NAME = 'МоиМосквин!B2:G30'

    @classmethod
    def handled_data(cls):
            values = cls.__get_data__()
            values = list(filter(lambda x: x[0] != '', values))  # удаляем строки с пробелами
            return values