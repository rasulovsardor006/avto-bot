from aiogram import F
from aiogram import Router
from django.db import transaction
from django.db.models import Avg, Min, Max
from aiogram import types
from apps.bot.models import Detection
from asgiref.sync import sync_to_async
from apps.bot.keyboards.inline import create_detection_keyboard
from apps.bot.utils.callback_data import MainMenuCallbackData, MainMenuAction, DetectionActiveMainMenuAction, \
    ActiveMainMenuCallbackData

router = Router()

@sync_to_async
def update_detection_status(detection_id, is_active=None, delete=False):
    try:
        with transaction.atomic():
            detection = Detection.objects.select_related('brand', 'model').get(id=detection_id)
            if delete:
                Detection.objects.filter(id=detection_id).delete()
                return True
            elif is_active is not None:
                detection.is_active = is_active
                detection.save(update_fields=['is_active'])
                return detection
    except Detection.DoesNotExist:
        return None

@sync_to_async
def get_user_detections(telegram_id):
    return list(Detection.objects.filter(user__telegram_id=telegram_id).select_related('brand', 'model'))

# Hisobot olish uchun asinxron funksiyasi
@sync_to_async
def get_detection_report(telegram_id):
    detections = Detection.objects.filter(user__telegram_id=telegram_id, is_active=True)

    if not detections:
        return None

    total_count = detections.count()

    avg_price = detections.aggregate(Avg('price'))['price__avg'] or 0

    min_price = detections.aggregate(Min('price'))['price__min'] or 0
    max_price = detections.aggregate(Max('price'))['price__max'] or 0

    best_ads = detections.order_by('price')[:3]

    report = {
        "total_count": total_count,
        "avg_price": avg_price,
        "min_price": min_price,
        "max_price": max_price,
        "best_ads": best_ads
    }

    return report

# Main menu callback: Faol detektsiyalarni ko'rsatish
@router.callback_query(MainMenuCallbackData.filter(F.action == MainMenuAction.ACTIVE))
async def main_menu_callback(callback_query: types.CallbackQuery):
    telegram_id = callback_query.from_user.id
    detections = await get_user_detections(telegram_id)

    if not detections:
        await callback_query.message.edit_text("❌ Sizning faol deteksiyalaringiz topilmadi.")
        return

    for detection in detections:
        detection_details = (
            f"🆔 ID: {detection.id}\n"
            f"🚗 Brande: {detection.brand.name}\n"
            f"🚗 Modeli: {detection.model.name}\n"
            f"🎨 Rang: {detection.color or 'Noma\'lum'}\n"
            f"📅 Yil: {detection.year_from or 'Noma\'lum'} - {detection.year_to or 'Noma\'lum'}"
        )
        inline_keyboard = create_detection_keyboard(detection)

        await callback_query.message.answer(
            detection_details,
            reply_markup=inline_keyboard.as_markup()
        )

    await callback_query.message.edit_text("📝 Sizning deteksiyalaringiz ro'yxati.")

# Deteksiyani faollashtirish
@router.callback_query(ActiveMainMenuCallbackData.filter(F.action == DetectionActiveMainMenuAction.ACTIVE))
async def activate_detection(callback_query: types.CallbackQuery, callback_data: MainMenuCallbackData):
    detection = await update_detection_status(callback_data.id, is_active=True)

    if detection:
        detection_details = (
            f"🆔 ID: {detection.id}\n"
            f"🚗 Brande: {detection.brand.name}\n"
            f"🚗 Modeli: {detection.model.name}\n"
            f"🎨 Rang: {detection.color or 'Noma\'lum'}\n"
            f"📅 Yil: {detection.year_from or 'Noma\'lum'} - {detection.year_to or 'Noma\'lum'}"
        )
        inline_keyboard = create_detection_keyboard(detection)
        await callback_query.message.edit_text(
            f"✅ Deteksiya faollashtirildi!\n{detection_details}",
            reply_markup=inline_keyboard.as_markup()
        )
    else:
        await callback_query.answer("❌ Deteksiya topilmadi.")

# Deteksiyani faolsizlantirish
@router.callback_query(ActiveMainMenuCallbackData.filter(F.action == DetectionActiveMainMenuAction.DEACTIVATED))
async def deactivate_detection(callback_query: types.CallbackQuery, callback_data: MainMenuCallbackData):
    detection = await update_detection_status(callback_data.id, is_active=False)

    if detection:
        detection_details = (
            f"🆔 ID: {detection.id}\n"
            f"🚗 Brande: {detection.brand.name}\n"
            f"🚗 Modeli: {detection.model.name}\n"
            f"🎨 Rang: {detection.color or 'Noma\'lum'}\n"
            f"📅 Yil: {detection.year_from or 'Noma\'lum'} - {detection.year_to or 'Noma\'lum'}"
        )
        inline_keyboard = create_detection_keyboard(detection)
        await callback_query.message.edit_text(
            f"❌ Deteksiya faolsizlantirildi!\n{detection_details}",
            reply_markup=inline_keyboard.as_markup()
        )
    else:
        await callback_query.answer("❌ Deteksiya topilmadi.")

@sync_to_async
def delete_detection_sync(detection_id):
    try:
        detection = Detection.objects.get(id=detection_id)
        detection.delete()
        return True
    except Detection.DoesNotExist:
        return False

@router.callback_query(ActiveMainMenuCallbackData.filter(F.action == DetectionActiveMainMenuAction.DELETED))
async def delete_detection(callback_query: types.CallbackQuery, callback_data: ActiveMainMenuCallbackData):
    detection_id = callback_data.id

    deletion_successful = await delete_detection_sync(detection_id)

    if deletion_successful:
        await callback_query.message.edit_text("✅ Deteksiya muvaffaqiyatli o'chirildi!", reply_markup=None)
    else:
        await callback_query.answer("❌ Deteksiya topilmadi yoki o'chirishda xato yuz berdi.")
