from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Structure, PaymentHistory, EditRequest


# -------------------------
# STEP 1
# -------------------------
@login_required
def structure_step1(request):

    TOWNS = [
        "Nsuta", "Beposo", "Kwamang", "Jeduako",
        "Bonkrong", "Amoamang", "Kyebi", "Atonsu",
        "Birem", "Kyeiase"
    ]

    if request.method == "POST":

        request.session["structure"] = {
            "town": request.POST.get("town"),
            "area": request.POST.get("area"),
            "latitude": request.POST.get("latitude"),
            "longitude": request.POST.get("longitude"),
        }

        return redirect("structure_step2")

    return render(request, "core/step1.html", {"towns": TOWNS})


# -------------------------
# STEP 2
# -------------------------
@login_required
def structure_step2(request):

    if "structure" not in request.session:
        return redirect("structure_step1")

    if request.method == "POST":

        data = request.session["structure"]

        data.update({
            "owner_name": request.POST.get("owner_name"),
            "owner_phone": request.POST.get("owner_phone"),
            "ghana_card": request.POST.get("ghana_card"),
        })

        request.session["structure"] = data
        return redirect("structure_step3")

    return render(request, "core/step2.html")


# -------------------------
# STEP 3 (INSPECTION ONLY - NO TS YET)
# -------------------------
@login_required
def structure_step3(request):

    if "structure" not in request.session:
        return redirect("structure_step1")

    if request.method == "POST":

        data = request.session["structure"]

        permit_status = request.POST.get("permit_status")

        data.update({
            "structure_type": request.POST.get("structure_type"),
            "permit_status": permit_status,
            "notes": request.POST.get("notes"),
        })

        request.session["structure"] = data

        # ALWAYS GO STEP 4 (NO PAYMENT HERE)
        return redirect("structure_step4")

    return render(request, "core/step3.html")


# -------------------------
# STEP 4 (CREATE TS + HANDLE PAYMENT ROUTING)
# -------------------------
@login_required
def structure_step4(request):

    if "structure" not in request.session:
        return redirect("structure_step1")

    data = request.session["structure"]

    if request.method == "POST":

        structure_photo = request.FILES.get("evidence_photo")

        if not structure_photo:
            return render(request, "core/step4.html", {
                "error": "Structure photo is required before submission",
                "data": data
            })

        # CREATE STRUCTURE (TS GENERATED HERE)
        structure = Structure.objects.create(
            collector=request.user,

            town=data["town"],
            area=data["area"],
            latitude=data["latitude"],
            longitude=data["longitude"],

            owner_name=data["owner_name"],
            owner_phone=data["owner_phone"],
            ghana_card=data["ghana_card"],

            structure_type=data["structure_type"],
            permit_status=data["permit_status"],
            notes=data["notes"],
        )

        structure.evidence_photo = structure_photo
        structure.save()

        # CLEAR SESSION
        request.session.pop("structure", None)

        # IF PAID → GO PAYMENT
        if structure.permit_status == "PAID":
            return redirect("record_payment_session", ts_id=structure.ts_id)

        return render(request, "core/success.html", {
            "ts_id": structure.ts_id,
            "name": structure.owner_name
        })

    return render(request, "core/step4.html", {"data": data})


# -------------------------
# PAYMENT SESSION (SAFE FIXED VERSION)
# -------------------------
@login_required
def record_payment_session(request, ts_id):

    structure = get_object_or_404(Structure, ts_id=ts_id)

    if request.method == "POST":

        receipt = request.FILES.get("receipt_photo")
        amount = request.POST.get("amount")

        if not receipt:
            return render(request, "core/payment.html", {
                "error": "Receipt is required",
                "structure": structure
            })

        PaymentHistory.objects.create(
            structure=structure,
            collector=request.user,
            receipt_photo=receipt,
            amount=amount,
            status="PENDING"
        )

        structure.permit_status = "PENDING"
        structure.save()

        return render(request, "core/payment_success.html", {
    "ts_id": structure.ts_id
})

    return render(request, "core/payment.html", {
        "structure": structure
    })


# -------------------------
# SEARCH
# -------------------------
@login_required
def structure_search(request):

    query = (request.GET.get("query") or "").strip()

    if query:
        result = Structure.objects.filter(
            Q(ts_id__icontains=query) |
            Q(owner_name__icontains=query) |
            Q(owner_phone__icontains=query)
        )
    else:
        result = Structure.objects.none()

    return render(request, "core/search.html", {
        "result": result,
        "query": query
    })


# -------------------------
# DETAIL VIEW
# -------------------------
@login_required
def structure_detail(request, ts_id):

    structure = get_object_or_404(Structure, ts_id=ts_id)

    return render(request, "core/detail.html", {
        "structure": structure
    })


# -------------------------
# LIST
# -------------------------
@login_required
def structure_list(request):

    structures = Structure.objects.filter(
        collector=request.user
    ).order_by("-id")

    return render(request, "core/list.html", {
        "structures": structures
    })


# -------------------------
# EDIT REQUEST
# -------------------------
@login_required
def request_edit(request, ts_id):

    structure = get_object_or_404(Structure, ts_id=ts_id)

    if request.method == "POST":

        field_name = request.POST.get("field_name")
        new_value = request.POST.get("new_value")
        reason = request.POST.get("reason")

        old_value = getattr(structure, field_name)

        if str(old_value) == str(new_value):
            return redirect("structure_list")

        EditRequest.objects.create(
            structure=structure,
            collector=request.user,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            reason=reason,
            status="PENDING"
        )

        return redirect("structure_list")

    return render(request, "core/edit_request.html", {
        "structure": structure
    })