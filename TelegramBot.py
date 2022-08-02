from calendar import month
import datetime
import logging
import json
from turtle import update
from matplotlib.pyplot import text
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)



def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Olá! Use /set <Nome do evento> <Horario> <data> para setar um novo alarme!'
        'Exemplo: /set Flauta_bday 12:00 05/12'
        )
    
def validateData(horario, date):
    if ':' not in horario:
        return False
    if '/' not in date:
        return False
    
    txtHora = horario.split(':')
    print(txtHora)
    hora = txtHora[0]
    min = txtHora[1]
    if(hora.isnumeric() == False | min.isnumeric() == False):
        return False
    if(int(hora) > 23) | (int(min) >= 60):
        return False
    txtDate = date.split('/')
    dia = txtDate[0]
    mes = txtDate[1]

    if(dia.isnumeric() == False | mes.isnumeric() == False):
        return False
    if (int(dia) >= 32) | (int(mes) > 12):
        print("Ah")
        return False
    return True

def set(update: Update, context: CallbackContext)-> int:
    name_event = context.args[0]
    horario = context.args[1]
    date = context.args[2]
    
    if len(context.args) < 3:
        update.message.reply_text('Hmmm.. acredito que voce digitou algo errado. Quer tentar de novo?\n'
        'Use /set <Nome do evento> <Horario> <data> para setar um novo alarme!')
        return

    if not validateData(horario, date):
        update.message.reply_text('Hmmm.. acredito que voce digitou algo errado. Quer tentar de novo?\n'
        'Use /set <Nome do evento> <Horario> <data> para setar um novo alarme!')
        return
    

    update.message.reply_text('Perfeitamente! O evento ' + name_event + ' foi adicionado para as ' + horario + 'h do dia ' + date)
    infos = {"name_event": name_event, "horario" : horario, "date" : date, "author": update.message.from_user.first_name, "chat_id" : update.message.chat_id}
    with open("info.json", 'a') as fp:
        json.dump(infos, fp)
        fp.write('\n')

def show(update: Update, context: CallbackContext)-> int:
    data = open('info.json','r')
    update.message.reply_text('Atenção! Seus proximos eventos sao:\n')

    counter = 0
    infosShow = ''
    for line in data:
        event_store = json.loads(line)
        infosShow += 'Evento: ' + event_store['name_event'] + ' no dia ' + event_store['date'] + ' às ' + event_store['horario'] + 'h\n'
        counter += 1
        if counter == 3:
            break
    update.message.reply_text(infosShow)

def convertDateTime(dateString, separator):
    txt = dateString.split(separator)
    return int(txt[0]), int(txt[1])

def removeEvent(pos):
    
    with open('info.json', "r+") as f:
        d = f.readlines()
        counter = 0
        f.seek(0)
        for i in d:
            if counter not in pos:
                f.write(i)
            counter += 1
        f.truncate()


def dateVerify(context):
    selectedHour = [7,3,1]
    dateNow = datetime.datetime.now()
    data = open('info.json','r')
    pos = 0
    remove = []
    for line in data:
        event_store = json.loads(line)
        dia, mes = convertDateTime(event_store['date'], '/')
        if(dia == dateNow.day) & (mes == dateNow.month):
            hora, min = convertDateTime(event_store['horario'], ':')
            if(abs(hora - dateNow.hour) in selectedHour):
                textReminder = 'Lembrete! Hoje há o evento marcado ' + event_store['name_event'] + ' às ' + event_store['horario'] + 'h'
                context.bot.send_message(chat_id= event_store['chat_id'], text=textReminder)
            if (hora <= dateNow.hour):
                if(min <= dateNow.minute):
                    textReminder = 'O evento '  + event_store['name_event'] + ' deve estar começando!! Contate os admins do canal para se manter informado!'
                    context.bot.send_message(chat_id= event_store['chat_id'], text=textReminder)
                    remove.append(pos)
    
        pos += 1
    data.close()
    removeEvent(remove)
def main() -> None:
    updater = Updater("5414205278:AAHZiwxErrwklPi6YXv9ik5EqsjDuJdakPI")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("set", set))
    dispatcher.add_handler(CommandHandler("show", show))
    VerificationDate= updater.job_queue
    VerificationDate.run_repeating(dateVerify, interval= 10, first= 0)
    updater.start_polling()
    updater.idle()

    print('a')


if __name__ == '__main__':
    main()